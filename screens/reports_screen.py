from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
import jdatetime
from persian import fa
from datetime import date

PRIMARY = (0.0, 0.208, 0.400, 1)      # #003566
SECONDARY = (1.0, 0.765, 0.0, 1)      # #ffc300
WHITE = (1, 1, 1, 1)
DARK_TEXT = (0.12, 0.12, 0.12, 1)
LIGHT_BG = (0.96, 0.97, 0.98, 1)
CARD_BG = (1, 1, 1, 1)
GRAY_BTN = (0.85, 0.87, 0.90, 1)


class ReportsScreen(MDScreen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.current_days = 7
        self.build_ui()

    def build_ui(self):
        root = MDBoxLayout(orientation="vertical", md_bg_color=LIGHT_BG)

        # هدر
        header = MDBoxLayout(
            size_hint_y=None,
            height=dp(70),
            md_bg_color=PRIMARY,
            padding=(dp(12), dp(10), dp(12), dp(10)),
            spacing=dp(8)
        )

        back_btn = MDFlatButton(
            text=fa("بازگشت"),
            theme_text_color="Custom",
            text_color=WHITE,
            font_name="Vazir",
            size_hint=(None, None),
            size=(dp(80), dp(36)),
            line_color=WHITE,
            line_width=1,
            on_release=self.go_back
        )
        header.add_widget(back_btn)

        title = MDLabel(
            text=fa("گزارش فعالیت‌ها"),
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=WHITE,
            halign="right",
            valign="middle",
            size_hint_x=1,
            font_name="Vazir",
            bold=True
        )
        header.add_widget(title)
        header.add_widget(MDLabel(size_hint=(None, None), size=(dp(80), dp(36))))
        root.add_widget(header)

        # فیلتر هفتگی / ماهانه
        period_box = MDBoxLayout(
            size_hint_y=None,
            height=dp(56),
            padding=(dp(16), dp(10)),
            spacing=dp(10)
        )

        self.weekly_btn = MDRaisedButton(
            text=fa("هفتگی"),
            size_hint_x=1,
            md_bg_color=PRIMARY,
            text_color=WHITE,
            font_name="Vazir",
            elevation=1,
            on_release=lambda x: self.switch_period(7)
        )
        self.monthly_btn = MDRaisedButton(
            text=fa("ماهانه"),
            size_hint_x=1,
            md_bg_color=GRAY_BTN,
            text_color=DARK_TEXT,
            font_name="Vazir",
            elevation=0,
            on_release=lambda x: self.switch_period(30)
        )
        self.yearly_btn = MDRaisedButton(
            text=fa("سالانه"),
            size_hint_x=1,
            md_bg_color=GRAY_BTN,
            text_color=DARK_TEXT,
            font_name="Vazir",
            elevation=0,
            on_release=lambda x: self.switch_period("year")
        )
        self.goals_btn = MDRaisedButton(
            text=fa("اهداف"),
            size_hint_x=1,
            md_bg_color=GRAY_BTN,
            text_color=DARK_TEXT,
            font_name="Vazir",
            elevation=0,
            on_release=lambda x: self.switch_period("goals")
        )
        # چپ به راست: اهداف، سالانه، ماهانه، هفتگی (نمایش راست‌به‌چپ: هفتگی، ماهانه، سالانه، اهداف)
        period_box.add_widget(self.goals_btn)
        period_box.add_widget(self.yearly_btn)
        period_box.add_widget(self.monthly_btn)
        period_box.add_widget(self.weekly_btn)
        root.add_widget(period_box)

        self.content = MDBoxLayout(
            orientation="vertical",
            padding=(dp(16), dp(6), dp(16), dp(16)),
            spacing=dp(12)
        )
        root.add_widget(self.content)
        self.add_widget(root)

    def on_enter(self, *args):
        self.refresh()

    def switch_period(self, period):
        self.current_days = period
        buttons = {
            7: self.weekly_btn, 30: self.monthly_btn,
            "year": self.yearly_btn, "goals": self.goals_btn
        }
        for key, btn in buttons.items():
            if key == period:
                btn.md_bg_color = PRIMARY
                btn.text_color = WHITE
            else:
                btn.md_bg_color = GRAY_BTN
                btn.text_color = DARK_TEXT
        self.refresh()

    def refresh(self):
        self.content.clear_widgets()

        if self.current_days == "year":
            self.refresh_year()
            return
        if self.current_days == "goals":
            self.refresh_goals()
            return
        
        name = self.db.get_name() or fa("کاربر")
        report = self.db.get_report(self.current_days)

        total_score = sum(r["score"] for r in report) if report else 0
        max_score = self.current_days * 10
        percent = int((total_score / max_score) * 100) if max_score > 0 else 0

        # خلاصه
        summary = MDCard(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(100),
            radius=[16],
            elevation=1,
            md_bg_color=CARD_BG
        )
        summary.add_widget(MDLabel(
            text=fa(f"گزارش {name}"),
            font_style="H6",
            theme_text_color="Custom",
            text_color=DARK_TEXT,
            halign="right",
            font_name="Vazir",
            size_hint_y=None,
            height=dp(28)
        ))
        summary.add_widget(MDLabel(
            text=fa(f"امتیاز کل: {total_score} از {max_score}   |   موفقیت: {percent}%"),
            theme_text_color="Custom",
            text_color=PRIMARY,
            halign="right",
            font_name="Vazir",
            size_hint_y=None,
            height=dp(24)
        ))
        self.content.add_widget(summary)

        # لیست
        scroll = ScrollView(do_scroll_x=False)
        list_box = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(8)
        )
        list_box.bind(minimum_height=list_box.setter("height"))

        status_map = {
            "green": (("انجام شده ✓"), (0.15, 0.65, 0.35, 1)),
            "yellow": (("اضطراری"), SECONDARY),
            "red": (("انجام نشده ✗"), (0.85, 0.25, 0.25, 1)),
            "pending": (("در انتظار"), (0.55, 0.58, 0.62, 1)),
        }

        if report:
            for row in report:
                try:
                    year, month, day = map(int, row["date"].split("-"))
                    jalali = jdatetime.date.fromgregorian(year=year, month=month, day=day)
                    shamsi_date = jalali.strftime("%Y/%m/%d")
                except Exception:
                    shamsi_date = row["date"]

                status_text, status_color = status_map.get(
                    row["status"], (row["status"], DARK_TEXT)
                )

                item_card = MDCard(
                    size_hint_y=None,
                    height=dp(64),
                    padding=(dp(14), dp(10)),
                    radius=[14],
                    elevation=0,
                    md_bg_color=CARD_BG,
                    line_color=(0.90, 0.91, 0.93, 1),
                    line_width=1
                )
                item_box = MDBoxLayout(orientation="vertical", spacing=dp(3))
                item_box.add_widget(MDLabel(
                    text=fa(f"{shamsi_date}    {status_text}"),
                    font_name="Vazir",
                    theme_text_color="Custom",
                    text_color=status_color,
                    halign="right",
                    size_hint_y=None,
                    height=dp(26)
                ))
                item_box.add_widget(MDLabel(
                    text=fa(f"امتیاز: {row['score']}"),
                    font_name="Vazir",
                    theme_text_color="Custom",
                    text_color=(0.45, 0.48, 0.52, 1),
                    halign="right",
                    size_hint_y=None,
                    height=dp(20)
                ))
                item_card.add_widget(item_box)
                list_box.add_widget(item_card)
        else:
            list_box.add_widget(MDLabel(
                text=fa("هنوز گزارشی ثبت نشده"),
                halign="center",
                theme_text_color="Hint",
                font_name="Vazir",
                size_hint_y=None,
                height=dp(80)
            ))

        scroll.add_widget(list_box)
        self.content.add_widget(scroll)

    def refresh_year(self):
        name = self.db.get_name() or fa("کاربر")
        year = jdatetime.date.today().year

        month_names = [
            "", "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
        ]

        last_day = 30 if jdatetime.date(year, 12, 1).isleap() else 29
        start = jdatetime.date(year, 1, 1).togregorian()
        end = jdatetime.date(year, 12, last_day).togregorian()
        rows = self.db.get_report_range(
            date(start.year, start.month, start.day),
            date(end.year, end.month, end.day)
        )

        # گروه‌بندی بر اساس ماه شمسی
        stats = {m: {"green": 0, "yellow": 0, "red": 0, "score": 0} for m in range(1, 13)}
        for r in rows:
            if r["status"] not in ("green", "yellow", "red"):
                continue   # روزهای در حال انجام حساب نمی‌شن
            y, mo, d = map(int, r["date"].split("-"))
            jm = jdatetime.date.fromgregorian(year=y, month=mo, day=d).month
            stats[jm][r["status"]] += 1
            stats[jm]["score"] += r["score"]

        total_score = sum(s["score"] for s in stats.values())
        n_green = sum(s["green"] for s in stats.values())
        n_yellow = sum(s["yellow"] for s in stats.values())
        n_red = sum(s["red"] for s in stats.values())
        days_in_year = 366 if last_day == 30 else 365   # سال کبیسه شمسی
        max_score = days_in_year * 10
        percent = round((total_score / max_score) * 100, 1)

        # خلاصه سال
        summary = MDCard(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(6),
            size_hint_y=None,
            height=dp(130),
            radius=[16],
            elevation=1,
            md_bg_color=CARD_BG
        )
        summary.add_widget(MDLabel(
            text=fa(f"گزارش سالانه {name} - {year}"),
            font_style="H6",
            theme_text_color="Custom",
            text_color=DARK_TEXT,
            halign="right",
            font_name="Vazir",
            size_hint_y=None,
            height=dp(28)
        ))
        summary.add_widget(MDLabel(
            text=fa(f"امتیاز کل: {total_score} از {max_score}   |   موفقیت: {percent}%"),
            theme_text_color="Custom",
            text_color=PRIMARY,
            halign="right",
            font_name="Vazir",
            size_hint_y=None,
            height=dp(24)
        ))
        summary.add_widget(MDLabel(
            text=fa(f"سبز: {n_green}   |   زرد: {n_yellow}   |   قرمز: {n_red}"),
            theme_text_color="Custom",
            text_color=(0.45, 0.48, 0.52, 1),
            halign="right",
            font_name="Vazir",
            size_hint_y=None,
            height=dp(22)
        ))
        self.content.add_widget(summary)

        # لیست ماه‌ها
        scroll = ScrollView(do_scroll_x=False)
        list_box = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(8)
        )
        list_box.bind(minimum_height=list_box.setter("height"))

        has_data = False
        for m in range(1, 13):
            s = stats[m]
            days_cnt = s["green"] + s["yellow"] + s["red"]
            if days_cnt == 0:
                continue
            has_data = True
        has_data = False
        for m in range(1, 13):
            s = stats[m]
            days_cnt = s["green"] + s["yellow"] + s["red"]
            if days_cnt == 0:
                continue
            has_data = True

            # تعداد کل روزهای ماه شمسی
            if m <= 6:
                m_days = 31
            elif m <= 11:
                m_days = 30
            else:
                m_days = last_day
            m_max = m_days * 10
            m_percent = round((s["score"] / m_max) * 100, 1)


            card = MDCard(
                size_hint_y=None,
                height=dp(84),
                padding=(dp(14), dp(10)),
                radius=[14],
                elevation=0,
                md_bg_color=CARD_BG,
                line_color=(0.90, 0.91, 0.93, 1),
                line_width=1
            )
            box = MDBoxLayout(orientation="vertical", spacing=dp(3))
            box.add_widget(MDLabel(
                text=fa(f"{month_names[m]}    {m_percent}%"),
                font_name="Vazir",
                theme_text_color="Custom",
                text_color=PRIMARY,
                bold=True,
                halign="right",
                size_hint_y=None,
                height=dp(26)
            ))
            box.add_widget(MDLabel(
                text=fa(f"امتیاز: {s['score']} از {m_max}"),
                font_name="Vazir",
                theme_text_color="Custom",
                text_color=DARK_TEXT,
                halign="right",
                size_hint_y=None,
                height=dp(20)
            ))
            box.add_widget(MDLabel(
                text=fa(f"سبز: {s['green']}   |   زرد: {s['yellow']}   |   قرمز: {s['red']}"),
                font_name="Vazir",
                theme_text_color="Custom",
                text_color=(0.45, 0.48, 0.52, 1),
                halign="right",
                size_hint_y=None,
                height=dp(20)
            ))
            card.add_widget(box)
            list_box.add_widget(card)

        if not has_data:
            list_box.add_widget(MDLabel(
                text=fa("هنوز گزارشی برای امسال ثبت نشده"),
                halign="center",
                theme_text_color="Hint",
                font_name="Vazir",
                size_hint_y=None,
                height=dp(80)
            ))

        scroll.add_widget(list_box)
        self.content.add_widget(scroll)

    def refresh_goals(self):
        goals = self.db.get_done_goals()

        summary = MDCard(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(80),
            radius=[16],
            elevation=1,
            md_bg_color=CARD_BG
        )
        summary.add_widget(MDLabel(
            text=fa(f"اهداف انجام‌شده: {len(goals)}"),
            font_style="H6",
            theme_text_color="Custom",
            text_color=DARK_TEXT,
            halign="right",
            font_name="Vazir"
        ))
        self.content.add_widget(summary)

        scroll = ScrollView(do_scroll_x=False)
        list_box = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(8)
        )
        list_box.bind(minimum_height=list_box.setter("height"))

        if not goals:
            list_box.add_widget(MDLabel(
                text=fa("هنوز هدفی انجام نشده"),
                halign="center",
                theme_text_color="Hint",
                font_name="Vazir",
                size_hint_y=None,
                height=dp(80)
            ))
        else:
            for g in goals:
                try:
                    y, m, d = map(int, g["done_at"].split("-"))
                    shamsi = jdatetime.date.fromgregorian(year=y, month=m, day=d).strftime("%Y/%m/%d")
                except Exception:
                    shamsi = ""

                card = MDCard(
                    size_hint_y=None,
                    height=dp(64),
                    padding=(dp(14), dp(10)),
                    radius=[14],
                    elevation=0,
                    md_bg_color=CARD_BG,
                    line_color=(0.2, 0.7, 0.4, 0.4),
                    line_width=1
                )
                box = MDBoxLayout(orientation="vertical", spacing=dp(3))
                box.add_widget(MDLabel(
                    text=fa(f"✓ {g['title']}"),
                    font_name="Vazir",
                    theme_text_color="Custom",
                    text_color=(0.15, 0.65, 0.35, 1),
                    halign="right",
                    size_hint_y=None,
                    height=dp(26)
                ))
                box.add_widget(MDLabel(
                    text=fa(f"تاریخ انجام: {shamsi}"),
                    font_name="Vazir",
                    theme_text_color="Custom",
                    text_color=(0.45, 0.48, 0.52, 1),
                    halign="right",
                    size_hint_y=None,
                    height=dp(20)
                ))
                card.add_widget(box)
                list_box.add_widget(card)

        scroll.add_widget(list_box)
        self.content.add_widget(scroll)
        
    def go_back(self, *args):
        self.manager.current = "today"