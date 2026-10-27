from datetime import datetime, timedelta
from kivy.utils import platform


def request_permission():
    """درخواست اجازه نوتیفیکیشن (اندروید ۱۳ به بالا)"""
    if platform != "android":
        return
    try:
        from android.permissions import request_permissions
        request_permissions(["android.permission.POST_NOTIFICATIONS"])
    except Exception as e:
        print("permission error:", e)


def _next_time(weekday, hhmm):
    h, m = map(int, hhmm.split(":"))
    now = datetime.now()
    target = datetime(now.year, now.month, now.day, h, m)
    target += timedelta(days=(weekday - now.weekday()) % 7)
    if target <= now:
        target += timedelta(days=7)
    return int(target.timestamp() * 1000)


def schedule_all(db):
    """همه آلارم‌ها را پاک و از نو می‌سازد."""
    if platform != "android":
        return
    try:
        from jnius import autoclass
        activity = autoclass("org.kivy.android.PythonActivity").mActivity
        Receiver = autoclass("org.zistro.zistro.ReminderReceiver")

        Receiver.cancelAll(activity)

        name = db.get_name() or "کاربر"

        for act in db.get_all_activities():
            body = f"{name} عزیز، فعالیت «{act['title']}» سر رسیده و باید انجامش بدی."
            for d in str(act["recurrence"]).split(","):
                d = d.strip()
                if not d.isdigit():
                    continue
                wd = int(d)
                code = int(act["id"]) * 10 + wd
                when = _next_time(wd, act["time"])
                Receiver.schedule(
                    activity,
                    "زمان فعالیت رسید",
                    body,
                    code,
                    when,
                )
    except Exception as e:
        print("schedule error:", e)
