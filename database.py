import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path


class Database:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS profile (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                name TEXT DEFAULT 'کاربر'
            );

            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                time TEXT NOT NULL,
                recurrence TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS daily_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                is_done INTEGER DEFAULT 0,
                UNIQUE(activity_id, date),
                FOREIGN KEY(activity_id) REFERENCES activities(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS day_status (
                date TEXT PRIMARY KEY,
                status TEXT DEFAULT 'pending',
                score INTEGER DEFAULT 0,
                note TEXT
            );

                        CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                is_done INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                done_at TEXT
            );
            INSERT OR IGNORE INTO profile (id, name) VALUES (1, 'کاربر');
        """)
        self.conn.commit()

    # ---------- پروفایل ----------
    def get_name(self) -> str:
        row = self.conn.execute("SELECT name FROM profile WHERE id = 1").fetchone()
        return row["name"] if row else "کاربر"

    def set_name(self, name: str):
        self.conn.execute("UPDATE profile SET name = ? WHERE id = 1", (name.strip(),))
        self.conn.commit()

    def add_activity(self, title: str, time: str, recurrence: str):
        self.conn.execute(
            "INSERT INTO activities (title, time, recurrence, created_at) VALUES (?, ?, ?, ?)",
            (title.strip(), time, recurrence, date.today().isoformat())
        )
        self.conn.commit()

    def update_activity(self, activity_id: int, title: str, time: str, recurrence: str):
        self.conn.execute(
            "UPDATE activities SET title=?, time=?, recurrence=? WHERE id=?",
            (title.strip(), time, recurrence, activity_id)
        )
        self.conn.commit()

    def delete_activity(self, activity_id: int):
        self.conn.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
        self.conn.commit()

    def get_all_activities(self):
        cur = self.conn.execute("SELECT * FROM activities")
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in rows]

    def get_activity(self, activity_id: int):
        return self.conn.execute(
            "SELECT * FROM activities WHERE id = ?", (activity_id,)
        ).fetchone()

    def get_activities_for_date(self, target_date: date):
        weekday = target_date.weekday()
        target_str = target_date.isoformat()
        result = []
        for r in self.get_all_activities():
            # فعالیت قبل از روز ساخته‌شدنش وجود نداشته
            created = str(r.get("created_at") or "")[:10]
            if created and target_str < created:
                continue
            days = [int(d) for d in r["recurrence"].split(",") if d.strip().isdigit()]
            if weekday in days:
                result.append(r)
        return result

    def purge_status_before_first_activity(self):
        """وضعیت روزهای قبل از اولین فعالیت پاک می‌شود (تیک زرد دستی حفظ می‌شود)."""
        row = self.conn.execute(
            "SELECT MIN(substr(created_at, 1, 10)) AS d FROM activities"
        ).fetchone()
        first = row["d"] if row else None
        if first:
            self.conn.execute(
                "DELETE FROM day_status WHERE date < ? AND status != 'yellow'", (first,)
            )
        else:
            self.conn.execute("DELETE FROM day_status WHERE status != 'yellow'")
        self.conn.commit()

    # ---------- تکمیل فعالیت ----------
    def set_completion(self, activity_id: int, target_date: date, is_done: bool):
        date_str = target_date.isoformat()
        self.conn.execute("""
            INSERT INTO daily_completions (activity_id, date, is_done)
            VALUES (?, ?, ?)
            ON CONFLICT(activity_id, date) DO UPDATE SET is_done = excluded.is_done
        """, (activity_id, date_str, 1 if is_done else 0))
        self.conn.commit()
        self.recalculate_day_status(target_date)

    def is_activity_done(self, activity_id: int, target_date: date) -> bool:
        row = self.conn.execute(
            "SELECT is_done FROM daily_completions WHERE activity_id=? AND date=?",
            (activity_id, target_date.isoformat())
        ).fetchone()
        return bool(row and row["is_done"])

    # ---------- وضعیت روز ----------
    def set_emergency(self, target_date: date, note: str = ""):
        self.conn.execute("""
            INSERT INTO day_status (date, status, score, note)
            VALUES (?, 'yellow', 5, ?)
            ON CONFLICT(date) DO UPDATE SET 
                status = 'yellow', 
                score = 5, 
                note = excluded.note
        """, (target_date.isoformat(), note))
        self.conn.commit()

    def recalculate_day_status(self, target_date: date):
        date_str = target_date.isoformat()
        current = self.conn.execute(
            "SELECT status FROM day_status WHERE date = ?", (date_str,)
        ).fetchone()

        # اگر قبلاً زرد زده شده، دست نزن
        if current and current["status"] == "yellow":
            return

        activities = self.get_activities_for_date(target_date)
        if not activities:
            # روزی که دیگه فعالیتی نداره، وضعیت قدیمی‌ش پاک می‌شه
            self.conn.execute("DELETE FROM day_status WHERE date = ?", (date_str,))
            self.conn.commit()
            return

        all_done = all(
            self.is_activity_done(a["id"], target_date) for a in activities
        )

        if all_done:
            status, score = "green", 10
        elif target_date < date.today():
            status, score = "red", 0
        else:
            status, score = "pending", 0

        self.conn.execute("""
            INSERT INTO day_status (date, status, score)
            VALUES (?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET 
                status = excluded.status, 
                score = excluded.score
        """, (date_str, status, score))
        self.conn.commit()

    def get_day_status(self, target_date: date):
        self.recalculate_day_status(target_date)
        return self.conn.execute(
            "SELECT * FROM day_status WHERE date = ?", (target_date.isoformat(),)
        ).fetchone()

    def get_report(self, days: int = 7):
        end = date.today()
        start = end - timedelta(days=days - 1)
        return self.conn.execute("""
            SELECT * FROM day_status
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC
        """, (start.isoformat(), end.isoformat())).fetchall()
    
    def get_report_range(self, start: date, end: date):
        return self.conn.execute("""
            SELECT * FROM day_status
            WHERE date BETWEEN ? AND ?
            ORDER BY date
        """, (start.isoformat(), end.isoformat())).fetchall()

    # ---------- اهداف سالانه ----------
    def add_goal(self, title: str):
        title = title.strip()
        if not title:
            return
        self.conn.execute("INSERT INTO goals (title) VALUES (?)", (title,))
        self.conn.commit()

    def get_pending_goals(self):
        return self.conn.execute(
            "SELECT * FROM goals WHERE is_done = 0 ORDER BY id"
        ).fetchall()

    def get_done_goals(self):
        return self.conn.execute(
            "SELECT * FROM goals WHERE is_done = 1 ORDER BY done_at DESC, id DESC"
        ).fetchall()

    def complete_goal(self, goal_id: int):
        self.conn.execute(
            "UPDATE goals SET is_done = 1, done_at = ? WHERE id = ?",
            (date.today().isoformat(), goal_id)
        )
        self.conn.commit()

    def restore_goal(self, goal_id: int):
        self.conn.execute(
            "UPDATE goals SET is_done = 0, done_at = NULL WHERE id = ?", (goal_id,)
        )
        self.conn.commit()

    def delete_goal(self, goal_id: int):
        self.conn.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        self.conn.commit()
        
    def close(self):
        self.conn.close()