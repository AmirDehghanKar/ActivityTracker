from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from datetime import date
from persian import fa
import jdatetime
from kivymd.uix.button import MDIconButton
from kivymd.uix.dialog import MDDialog
from kivy.uix.widget import Widget
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivy.uix.floatlayout import FloatLayout


PRIMARY = (0.0, 0.208, 0.400, 1)       # #003566
SECONDARY = (1.0, 0.765, 0.0, 1)       # #ffc300
WHITE = (1, 1, 1, 1)
DARK_TEXT = (0.12, 0.12, 0.12, 1)
LIGHT_BG = (0.96, 0.97, 0.98, 1)
CARD_BG = (1, 1, 1, 1)
GRAY_BTN = (0.93, 0.94, 0.96, 1)


class TodayScreen(MDScreen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.today = date.today()
        today_j = jdatetime.date.today()
        self.cal_year = today_j.year
        self.cal_month = today_j.month
        self.build_ui()

    def build_ui(self):
        root = MDBoxLayout(orientation="vertical", md_bg_color=LIGHT_BG)

        # ========== هدر ==========
        header = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(120),
            md_bg_color=PRIMARY,
            padding=(dp(16), dp(10), dp(16), dp(12)),
            spacing=dp(8)
        )

        top_row = MDBoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))

        report_btn = MDFlatButton(
            text=fa("گزارش"),
            theme_text_color="Custom",
            text_color=WHITE,
            font_name="Vazir",
            size_hint=(None, None),
            size=(dp(72), dp(34)),
            line_color=WHITE,
            line_width=1,
            on_release=self.go_to_reports
        )
        top_row.add_widget(report_btn)

        # عنوان ZISTRO وسط‌چین افقی و عمودی + رنگ زرد
        title = MDLabel(
            text="ZISTRO",
            font_style="H5",
            theme_text_color="Custom",
            text_color=SECONDARY,          # رنگ زرد فرعی
            halign="center",
            valign="center",
            size_hint_x=1,
            bold=True
        )
        title.bind(size=title.setter("text_size"))   # برای وسط‌چین عمودی بهتر
        top_row.add_widget(title)

        profile_btn = MDFlatButton(
            text=fa("پروفایل"),
            theme_text_color="Custom",
            text_color=WHITE,
            font_name="Vazir",
            size_hint=(None, None),
            size=(dp(72), dp(34)),
            line_color=WHITE,
            line_width=1,
            on_release=self.go_to_profile
        )
        top_row.add_widget(profile_btn)
        header.add_widget(top_row)

        # کارت وضعیت + تاریخ شمسی زنده (چپ)
        self.status_card = MDCard(
            size_hint_y=None,
            height=dp(58),
            padding=(dp(14), dp(6)),
            radius=[14],
            elevation=0,
            md_bg_color=(1, 1, 1, 0.15)
        )
        self.status_row = MDBoxLayout(orientation="horizontal")
        self.status_card.add_widget(self.status_row)
        header.add_widget(self.status_card)
        root.add_widget(header)

        # ========== محتوای اسکرول ==========
        scroll = ScrollView(do_scroll_x=False)
        self.main_content = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(12),
            padding=(dp(14), dp(14), dp(14), dp(90))
        )
        self.main_content.bind(minimum_height=self.main_content.setter("height"))

        # لیست فعالیت‌ها
        self.activity_list = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(10)
        )
        self.activity_list.bind(minimum_height=self.activity_list.setter("height"))
        self.main_content.add_widget(self.activity_list)

        # تقویم شمسی
        self.calendar_card = MDCard(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(6),
            size_hint_y=None,
            height=dp(310),
            radius=[16],
            elevation=1,
            md_bg_color=CARD_BG
        )
        self.main_content.add_widget(self.calendar_card)

        # اهداف سالانه
        self.goals_card = MDCard(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(6),
            size_hint_y=None,
            height=dp(120),
            radius=[16],
            elevation=1,
            md_bg_color=CARD_BG
        )
        self.main_content.add_widget(self.goals_card)

        # برنامه هفتگی
        self.week_plan_card = MDCard(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(4),
            size_hint_y=None,
            height=dp(260),
            radius=[16],
            elevation=1,
            md_bg_color=CARD_BG
        )
        self.main_content.add_widget(self.week_plan_card)

        scroll.add_widget(self.main_content)
        root.add_widget(scroll)

        # ========== نوار پایین (دکمه‌ها وسط‌چین) ==========
        bottom_bar = MDBoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=(dp(8), dp(10)),
            spacing=dp(8),
            md_bg_color=WHITE
        )

        BTN_W = dp(112)   # عرض هر دکمه
        BTN_H = dp(40)

        # فنر چپ
        bottom_bar.add_widget(Widget())

        self.emergency_btn = MDRaisedButton(
            text=fa("روز اضطراری"),
            md_bg_color=SECONDARY,
            text_color=DARK_TEXT,
            font_name="Vazir",
            font_size="12sp",
            size_hint=(None, None),
            size=(BTN_W, BTN_H),
            pos_hint={"center_y": 0.5},
            elevation=1,
            on_release=self.set_emergency
        )
        bottom_bar.add_widget(self.emergency_btn)

        add_btn = MDRaisedButton(
            text=fa("افزودن"),
            md_bg_color=PRIMARY,
            text_color=WHITE,
            font_name="Vazir",
            font_size="12sp",
            size_hint=(None, None),
            size=(BTN_W, BTN_H),
            pos_hint={"center_y": 0.5},
            elevation=1,
            on_release=self.go_to_add
        )
        bottom_bar.add_widget(add_btn)

        manage_btn = MDRaisedButton(
            text=fa("مدیریت فعالیت"),
            md_bg_color=(0.78, 0.82, 0.88, 1),
            text_color=PRIMARY,
            font_name="Vazir",
            font_size="12sp",
            size_hint=(None, None),
            size=(BTN_W, BTN_H),
            pos_hint={"center_y": 0.5},
            elevation=1,
            on_release=self.go_to_manage
        )
        bottom_bar.add_widget(manage_btn)
        # فنر راست
        bottom_bar.add_widget(Widget())

        root.add_widget(bottom_bar)
        self.add_widget(root)

    def on_enter(self, *args):
        self.refresh()

    def refresh(self):
        self.update_status_card()
        self.update_activities()
        self.build_calendar()
        self.build_goals()
        self.build_week_plan()

    def update_status_card(self):
        self.status_row.clear_widgets()

        today_j = jdatetime.date.today()
        wd_names = {
            0: fa("شنبه"), 1: fa("یکشنبه"), 2: fa("دوشنبه"),
            3: fa("سه‌شنبه"), 4: fa("چهارشنبه"), 5: fa("پنج‌شنبه"), 6: fa("جمعه")
        }
        live_date = f"{wd_names.get(today_j.weekday(), '')}  {today_j.strftime('%Y/%m/%d')}"

        # تاریخ شمسی چپ‌چین
        date_lbl = MDLabel(
            text=live_date,
            theme_text_color="Custom",
            text_color=WHITE,
            halign="left",
            font_name="Vazir",
            size_hint_x=0.42
        )
        self.status_row.add_widget(date_lbl)

        # وضعیت و امتیاز راست‌چین
        right = MDBoxLayout(orientation="vertical", spacing=dp(2), size_hint_x=0.58)

        status = self.db.get_day_status(self.today)
        if status:
            status_map = {
                "green":   (("انجام شده ✓"), 10, (0.15, 0.65, 0.35, 1)),
                "yellow":  (("اضطراری"), 5, SECONDARY),
                "red":     (("انجام نشده ✗"), 0, (0.85, 0.25, 0.25, 1)),
                "pending": (("در حال انجام"), "—", (0.55, 0.58, 0.62, 1)),
            }
            text, score, color = status_map.get(
                status["status"],
                (("نامشخص"), "—", (0.5, 0.5, 0.5, 1))
            )
        else:
            text, score, color = ("در حال انجام"), "—", (0.55, 0.58, 0.62, 1)

        self.status_label = MDLabel(
            text=fa(f"وضعیت: {text}"),
            theme_text_color="Custom",
            text_color=WHITE,
            halign="right",
            font_name="Vazir",
            size_hint_y=None,
            height=dp(24)
        )
        self.score_label = MDLabel(
            text=fa(f"امتیاز: {score}"),
            theme_text_color="Custom",
            text_color=SECONDARY,
            halign="right",
            font_name="Vazir",
            size_hint_y=None,
            height=dp(22)
        )
        right.add_widget(self.status_label)
        right.add_widget(self.score_label)
        self.status_row.add_widget(right)

    def update_activities(self):
        self.activity_list.clear_widgets()
        activities = self.db.get_activities_for_date(self.today)

        if not activities:
            self.activity_list.add_widget(MDLabel(
                text=fa("هیچ فعالیتی برای امروز تعریف نشده"),
                halign="center",
                theme_text_color="Hint",
                font_name="Vazir",
                size_hint_y=None,
                height=dp(90)
            ))
            return

        for act in activities:
            is_done = self.db.is_activity_done(act["id"], self.today)

            card = MDCard(
                size_hint_y=None,
                height=dp(68),
                padding=(dp(14), dp(10)),
                radius=[16],
                elevation=1,
                md_bg_color=CARD_BG,
                line_color=(0.88, 0.90, 0.92, 1) if not is_done else (0.2, 0.7, 0.4, 0.4),
                line_width=1.5
            )

            row = MDBoxLayout(orientation="horizontal", spacing=dp(12))

            check_btn = MDCard(
                size_hint=(None, None),
                size=(dp(22), dp(22)),
                pos_hint={"center_y": 0.5},
                radius=[dp(11)],
                elevation=0,
                md_bg_color=(0.15, 0.65, 0.35, 1) if is_done else (1, 1, 1, 1),
                line_color=(0.15, 0.65, 0.35, 1) if is_done else PRIMARY,
                line_width=1.2,
                ripple_behavior=True,
                on_release=lambda x, a_id=act["id"], done=is_done: self.toggle_done(a_id, not done)
            )
            if is_done:
                check_btn.add_widget(MDLabel(
                    text="✓",
                    halign="center",
                    valign="middle",
                    theme_text_color="Custom",
                    text_color=WHITE,
                    bold=True,
                    font_size="13sp"
                ))
            row.add_widget(check_btn)


            text_box = MDBoxLayout(orientation="vertical", spacing=dp(2))
            text_box.add_widget(MDLabel(
                text=fa(act["title"]),
                font_name="Vazir",
                halign="right",
                theme_text_color="Custom",
                text_color=DARK_TEXT,
                font_style="Subtitle1",
                bold=True
            ))
            text_box.add_widget(MDLabel(
                text=fa(act["time"]),
                font_name="Vazir",
                halign="right",
                theme_text_color="Custom",
                text_color=(0.45, 0.48, 0.52, 1),
                font_style="Caption"
            ))
            row.add_widget(text_box)
            card.add_widget(row)
            self.activity_list.add_widget(card)

    def toggle_done(self, activity_id, is_done):
        self.db.set_completion(activity_id, self.today, is_done)
        self.refresh()

    def set_emergency(self, *args):
        self.db.set_emergency(self.today)
        self.refresh()

    def go_to_add(self, *args):
        self.manager.current = "add_edit"
        self.manager.get_screen("add_edit").load_for_add()

    def go_to_manage(self, *args):
        self.manager.current = "manage"
   
    def go_to_reports(self, *args):
        self.manager.current = "reports"

    def go_to_profile(self, *args):
        self.manager.current = "profile"

    # ==================== تقویم شمسی ====================
    def change_month(self, delta):
        m = self.cal_month + delta
        y = self.cal_year
        if m < 1:
            m = 12
            y -= 1
        elif m > 12:
            m = 1
            y += 1
        self.cal_year = y
        self.cal_month = m
        self.build_calendar()
    def build_calendar(self):
        self.calendar_card.clear_widgets()

        month_names = [
            "", fa("فروردین"), fa("اردیبهشت"), fa("خرداد"),
            fa("تیر"), fa("مرداد"), fa("شهریور"),
            fa("مهر"), fa("آبان"), fa("آذر"),
            fa("دی"), fa("بهمن"), fa("اسفند")
        ]

        # هدر ماه (راست‌به‌چپ: قبلی سمت راست، بعدی سمت چپ)
        mh = MDBoxLayout(size_hint_y=None, height=dp(38), spacing=dp(4))

        next_btn = MDFlatButton(
            text=fa("<<<"),
            theme_text_color="Custom",
            text_color=PRIMARY,
            font_name="Vazir",
            size_hint=(None, None),
            size=(dp(64), dp(34)),
            on_release=lambda x: self.change_month(1)
        )
        prev_btn = MDFlatButton(
            text=fa(">>>"),
            theme_text_color="Custom",
            text_color=PRIMARY,
            font_name="Vazir",
            size_hint=(None, None),
            size=(dp(64), dp(34)),
            on_release=lambda x: self.change_month(-1)
        )
        ml = MDLabel(
            text=month_names[self.cal_month],      # فقط نام ماه، بدون سال
            font_name="Vazir",
            halign="center",
            theme_text_color="Custom",
            text_color=PRIMARY,
            bold=True
        )
        mh.add_widget(next_btn)   # چپ
        mh.add_widget(ml)         # وسط
        mh.add_widget(prev_btn)   # راست
        self.calendar_card.add_widget(mh)

        # نام روزهای هفته: شنبه سمت راست
        wd_row = MDBoxLayout(size_hint_y=None, height=dp(24), spacing=0)
        wd_labels = [fa("ش"), fa("ی"), fa("د"), fa("س"), fa("چ"), fa("پ"), fa("ج")]
        for n in reversed(wd_labels):
            wd_row.add_widget(MDLabel(
                text=n,
                size_hint_x=1,
                halign="center",
                font_name="Vazir",
                theme_text_color="Custom",
                text_color=PRIMARY,
                font_style="Caption",
                bold=True
            ))
        self.calendar_card.add_widget(wd_row)

        # تعداد روز ماه
        if self.cal_month <= 6:
            dim = 31
        elif self.cal_month <= 11:
            dim = 30
        else:
            dim = 30 if jdatetime.date(self.cal_year, 12, 1).isleap() else 29

        first = jdatetime.date(self.cal_year, self.cal_month, 1)
        start_wd = first.weekday()  # شنبه = 0 ... جمعه = 6

        today_j = jdatetime.date.today()
        day_num = 1
        for week in range(6):
            if day_num > dim:
                break

            week_box = MDBoxLayout(size_hint_y=None, height=dp(28), spacing=0)
            cells = []   # از شنبه تا جمعه

            for wd in range(7):
                if (week == 0 and wd < start_wd) or day_num > dim:
                    cells.append(MDLabel(text="", size_hint_x=1))
                    continue

                g = jdatetime.date(self.cal_year, self.cal_month, day_num).togregorian()
                g_date = date(g.year, g.month, g.day)

                acts = self.db.get_activities_for_date(g_date)
                has_plan = len(acts) > 0
                st = self.db.get_day_status(g_date)

                color = DARK_TEXT

                # فقط روزهای گذشته رنگ وضعیت بگیرند
                if g_date < self.today and st:
                    try:
                        s = st["status"]
                    except Exception:
                        s = None

                    if s == "green":
                        color = (0.15, 0.65, 0.35, 1)
                    elif s == "yellow":
                        color = (0.95, 0.70, 0.0, 1)
                    elif s == "red":
                        color = (0.85, 0.20, 0.20, 1)
                # امروز/آینده با برنامه → سرمه‌ای
                elif has_plan:
                    color = PRIMARY

                # امروز پررنگ‌تر
                if (self.cal_year == today_j.year and
                        self.cal_month == today_j.month and
                        day_num == today_j.day):
                    color = PRIMARY

                cells.append(MDLabel(
                    text=str(day_num),
                    size_hint_x=1,
                    halign="center",
                    valign="center",
                    font_name="Vazir",
                    theme_text_color="Custom",
                    text_color=color,
                    bold=True if color == PRIMARY else False,
                    font_size="12sp"
                ))
                day_num += 1

            # برعکس اضافه می‌کنیم تا شنبه سمت راست قرار بگیره
            for c in reversed(cells):
                week_box.add_widget(c)

            self.calendar_card.add_widget(week_box)

        # راهنما
        self.calendar_card.add_widget(MDLabel(
            text=fa("سبز: انجام‌شده  |  زرد: اضطراری  |  قرمز: انجام‌نشده"),
            font_name="Vazir",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(0.45, 0.48, 0.52, 1),
            halign="center",
            size_hint_y=None,
            height=dp(22)
        ))

            # ==================== اهداف سالانه ====================
    def build_goals(self):
        self.goals_card.clear_widgets()
        goals = self.db.get_pending_goals()

        # هدر: دکمه افزودن (چپ) + عنوان (راست)
        head = MDBoxLayout(size_hint_y=None, height=dp(36), spacing=dp(6))
        add_btn = MDRaisedButton(
            text=fa("افزودن هدف"),
            md_bg_color=PRIMARY,
            text_color=WHITE,
            font_name="Vazir",
            font_size="12sp",
            size_hint=(None, None),
            size=(dp(96), dp(32)),
            pos_hint={"center_y": 0.5},
            elevation=0,
            on_release=self.open_add_goal
        )
        head.add_widget(add_btn)
        head.add_widget(MDLabel(
            text=fa("اهداف سالانه"),
            font_name="Vazir",
            theme_text_color="Custom",
            text_color=PRIMARY,
            halign="right",
            valign="middle",
            bold=True
        ))
        self.goals_card.add_widget(head)

        row_h = dp(40)
        if not goals:
            self.goals_card.add_widget(MDLabel(
                text=fa("هدفی ثبت نشده."),
                font_name="Vazir",
                theme_text_color="Hint",
                halign="center",
                font_size="10sp",
                size_hint_y=None,
                height=dp(36)
            ))
            self.goals_card.height = dp(12 * 2 + 36 + 6 + 36)
            return

        for g in goals:
            row = MDBoxLayout(
                size_hint_y=None,
                height=row_h,
                spacing=dp(8)
            )

            # تیک (چپ): دایره کوچک
            check_btn = MDCard(
                size_hint=(None, None),
                size=(dp(20), dp(20)),
                pos_hint={"center_y": 0.5},
                radius=[dp(10)],
                elevation=0,
                md_bg_color=(1, 1, 1, 1),
                line_color=PRIMARY,
                line_width=1.2,
                ripple_behavior=True,
                on_release=lambda x, gid=g["id"]: self.complete_goal(gid)
            )
            row.add_widget(check_btn)

            # حذف
            del_btn = MDFlatButton(
                text=fa("حذف"),
                theme_text_color="Custom",
                text_color=(0.85, 0.25, 0.25, 1),
                font_name="Vazir",
                font_size="12sp",
                size_hint=(None, None),
                size=(dp(48), dp(34)),
                pos_hint={"center_y": 0.5},
                on_release=lambda x, gid=g["id"], t=g["title"]: self.confirm_delete_goal(gid, t)
            )
            row.add_widget(del_btn)

            # عنوان (راست‌چین)
            title_lbl = MDLabel(
                text=fa(g["title"]),
                font_name="Vazir",
                halign="right",
                valign="middle",
                theme_text_color="Custom",
                text_color=DARK_TEXT,
                shorten=True,
                shorten_from="right"
            )
            title_lbl.bind(size=lambda inst, s: setattr(inst, "text_size", s))
            row.add_widget(title_lbl)

            self.goals_card.add_widget(row)

        n = len(goals)
        # پدینگ ۲۴ + هدر ۳۶ + (n ردیف) + فاصله‌ها
        self.goals_card.height = dp(24 + 36) + n * row_h + n * dp(6)

    def open_add_goal(self, *args):
        # فیلد شفاف + لیبل پیش‌نمایش روی آن (مثل صفحه افزودن فعالیت)
        input_box = FloatLayout(size_hint_y=None, height=dp(52))

        self.goal_input = MDTextField(
            mode="rectangle",
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0},
            font_name="Vazir",
            multiline=False,
            line_color_normal=PRIMARY,
            line_color_focus=PRIMARY,
        )
        self.goal_input.foreground_color = (1, 1, 1, 0)
        self.goal_input.text_color_normal = (1, 1, 1, 0)
        self.goal_input.text_color_focus = (1, 1, 1, 0)
        input_box.add_widget(self.goal_input)

        self.goal_preview = MDLabel(
            text="",
            font_name="Vazir",
            halign="right",
            valign="center",
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0},
            padding=(dp(12), 0, dp(12), 0),
            theme_text_color="Custom",
            text_color=DARK_TEXT
        )
        input_box.add_widget(self.goal_preview)

        self.goal_input.bind(
            text=lambda inst, v: setattr(
                self.goal_preview, "text", fa(v) if v.strip() else ""
            )
        )

        box = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(70),
            padding=(0, dp(8), 0, 0)
        )
        box.add_widget(input_box)

        self.goal_dialog = MDDialog(
            title=fa("هدف جدید"),
            type="custom",
            content_cls=box,
            buttons=[
                MDFlatButton(
                    text=fa("انصراف"),
                    theme_text_color="Custom",
                    text_color=PRIMARY,
                    font_name="Vazir",
                    on_release=lambda x: self.goal_dialog.dismiss()
                ),
                MDRaisedButton(
                    text=fa("ذخیره"),
                    md_bg_color=PRIMARY,
                    text_color=WHITE,
                    font_name="Vazir",
                    on_release=self.save_goal
                ),
            ]
        )
        self.goal_dialog.open()

    def save_goal(self, *args):
        title = self.goal_input.text.strip()
        if title:
            self.db.add_goal(title)
        self.goal_dialog.dismiss()
        self.build_goals()

    def complete_goal(self, goal_id):
        self.db.complete_goal(goal_id)
        self.build_goals()

    def confirm_delete_goal(self, goal_id, title):
        self.del_goal_dialog = MDDialog(
            text=fa(f"هدف «{title}» حذف شود؟"),
            buttons=[
                MDFlatButton(
                    text=fa("انصراف"),
                    theme_text_color="Custom",
                    text_color=PRIMARY,
                    font_name="Vazir",
                    on_release=lambda x: self.del_goal_dialog.dismiss()
                ),
                MDRaisedButton(
                    text=fa("حذف"),
                    md_bg_color=(0.85, 0.25, 0.25, 1),
                    text_color=WHITE,
                    font_name="Vazir",
                    on_release=lambda x: self._do_delete_goal(goal_id)
                ),
            ]
        )
        self.del_goal_dialog.open()

    def _do_delete_goal(self, goal_id):
        self.del_goal_dialog.dismiss()
        self.db.delete_goal(goal_id)
        self.build_goals()

    # ==================== برنامه هفتگی ====================
    def build_week_plan(self):
        self.week_plan_card.clear_widgets()

        self.week_plan_card.add_widget(MDLabel(
            text=fa("برنامه هفتگی فعالیت‌ها"),
            font_name="Vazir",
            theme_text_color="Custom",
            text_color=PRIMARY,
            halign="right",
            bold=True,
            size_hint_y=None,
            height=dp(28)
        ))

        day_names = {
            0: "دوشنبه", 1: "سه‌شنبه", 2: "چهارشنبه", 3: "پنج‌شنبه",
            4: "جمعه", 5: "شنبه", 6: "یکشنبه",
        }

        try:
            all_acts = self.db.get_all_activities()
        except Exception:
            all_acts = []

        # شمارش فعالیت هر روز
        counts = {i: 0 for i in range(7)}
        for act in all_acts:
            for d in str(act.get("recurrence", "")).split(","):
                d = d.strip()
                if d.isdigit() and int(d) in counts:
                    counts[int(d)] += 1

        today_wd = date.today().weekday()

        for day_num in (5, 6, 0, 1, 2, 3, 4):   # شنبه تا جمعه
            count = counts[day_num]
            is_today = (day_num == today_wd)

            row_card = MDCard(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(26),
                padding=(dp(8), 0),
                radius=[10],
                elevation=0,
                md_bg_color=(0.0, 0.208, 0.400, 0.07) if is_today else (0, 0, 0, 0)
            )

            # سمت چپ: نشان تعداد
            badge_box = MDBoxLayout(
                size_hint_x=0.3,
                padding=(0, dp(2), 0, dp(2))
            )
            badge_box.add_widget(self._make_count_badge(count))
            badge_box.add_widget(Widget())
            row_card.add_widget(badge_box)

            # سمت راست: نام روز
            row_card.add_widget(MDLabel(
                text=fa(day_names[day_num]),
                font_name="Vazir",
                theme_text_color="Custom",
                text_color=PRIMARY if is_today else SECONDARY,
                halign="right",
                valign="middle",
                bold=True,
                size_hint_x=0.7,
                font_size="12sp"
            ))

            self.week_plan_card.add_widget(row_card)

    def _make_count_badge(self, count):
        """نشان گرد: زرد با عدد برای روز دارای فعالیت، خاکستری برای روز خالی"""
        if count > 0:
            bg = SECONDARY
            fg = DARK_TEXT
            txt = str(count)
        else:
            bg = (0.90, 0.91, 0.93, 1)
            fg = (0.55, 0.58, 0.62, 1)
            txt = "0"

        badge = MDCard(
            size_hint=(None, None),
            size=(dp(22), dp(22)),
            radius=[dp(11)],
            elevation=0,
            md_bg_color=bg
        )
        badge.add_widget(MDLabel(
            text=txt,
            font_name="Vazir",
            theme_text_color="Custom",
            text_color=fg,
            halign="center",
            valign="middle",
            bold=count > 0,
            font_size="11sp"
        ))
        return badge
        row.add_widget(day_lbl)

        self.week_plan_card.add_widget(row)