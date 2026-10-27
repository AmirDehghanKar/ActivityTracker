from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from persian import fa
import reminders

# رنگ‌ها
PRIMARY = (0.0, 0.208, 0.400, 1)       # #003566
SECONDARY = (1.0, 0.765, 0.0, 1)       # #ffc300
WHITE = (1, 1, 1, 1)
DARK_TEXT = (0.12, 0.12, 0.12, 1)
LIGHT_BG = (0.96, 0.97, 0.98, 1)
CARD_BG = (1, 1, 1, 1)
GRAY_BTN = (0.92, 0.93, 0.95, 1)


class AddEditScreen(MDScreen):

        def __init__(self, db, **kwargs):
                    super().__init__(**kwargs)
                    self.db = db
                    self.editing_id = None
                    self.return_to = "today"                    
                    self.day_buttons = {}
                    self.build_ui()

        def build_ui(self):
            root = MDBoxLayout(orientation="vertical", md_bg_color=LIGHT_BG)

            # ========== هدر ==========
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

            self.toolbar_title = MDLabel(
                text=fa("افزودن فعالیت"),
                font_style="H6",
                theme_text_color="Custom",
                text_color=WHITE,
                halign="right",
                valign="middle",
                size_hint_x=1,
                font_name="Vazir",
                bold=True
            )
            header.add_widget(self.toolbar_title)

            # فضای خالی برای تعادل
            header.add_widget(MDLabel(size_hint=(None, None), size=(dp(80), dp(36))))
            root.add_widget(header)

            # ========== محتوای اسکرول‌پذیر ==========
            scroll = ScrollView(do_scroll_x=False)
            content = MDBoxLayout(
                orientation="vertical",
                size_hint_y=None,
                padding=(dp(16), dp(14), dp(16), dp(20)),
                spacing=dp(12)
            )
            content.bind(minimum_height=content.setter("height"))

            # --- کارت عنوان ---
            title_card = MDCard(
                orientation="vertical",
                padding=dp(16),
                spacing=dp(8),
                size_hint_y=None,
                height=dp(123),
                radius=[16],
                elevation=1,
                md_bg_color=CARD_BG
            )
            title_card.add_widget(MDLabel(
                text=fa("عنوان فعالیت"),
                font_style="Subtitle2",
                theme_text_color="Custom",
                text_color=DARK_TEXT,
                halign="right",
                font_name="Vazir",
                size_hint_y=None,
                height=dp(50)
            ))

            title_box = FloatLayout(size_hint_y=None, height=dp(52))
            self.title_input = MDTextField(
                mode="rectangle",
                size_hint=(1, 1),
                pos_hint={"x": 0, "y": 0},
                font_name="Vazir",
                multiline=False,
                line_color_normal=PRIMARY,
                line_color_focus=PRIMARY,
            )
            self.title_input.foreground_color = (1, 1, 1, 0)
            self.title_input.text_color_normal = (1, 1, 1, 0)
            self.title_input.text_color_focus = (1, 1, 1, 0)
            self.title_input.bind(text=self.on_title_text)
            title_box.add_widget(self.title_input)

            self.title_preview = MDLabel(
                text="",
                font_name="Vazir",
                font_style="Body1",
                halign="right",
                valign="center",
                size_hint=(1, 1),
                pos_hint={"x": 0, "y": 0},
                padding=(dp(12), 0, dp(12), 0),
                theme_text_color="Custom",
                text_color=DARK_TEXT
            )
            title_box.add_widget(self.title_preview)
            title_card.add_widget(title_box)
            content.add_widget(title_card)

            # --- کارت زمان ---
            time_card = MDCard(
                orientation="vertical",
                padding=dp(16),
                spacing=dp(6),
                size_hint_y=None,
                height=dp(145),
                radius=[16],
                elevation=1,
                md_bg_color=CARD_BG
            )
            time_card.add_widget(MDLabel(
                text=fa("زمان فعالیت"),
                font_style="Subtitle2",
                theme_text_color="Custom",
                text_color=DARK_TEXT,
                halign="right",
                font_name="Vazir",
                size_hint_y=None,
                height=dp(24)
            ))

            self.time_input = MDTextField(
                mode="rectangle",
                size_hint_x=1,
                font_name="Vazir",
                input_filter="int",
                line_color_normal=PRIMARY,
                line_color_focus=PRIMARY,
            )
            self.time_input.bind(text=self.on_time_text)
            time_card.add_widget(self.time_input)

            time_card.add_widget(MDLabel(
                text=fa("فرمت ۲۴ ساعته (مثال: 21:30)"),
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.5, 0.52, 0.55, 1),
                halign="right",
                font_name="Vazir",
                size_hint_y=None,
                height=dp(20)
            ))
            content.add_widget(time_card)

            # --- کارت روزهای تکرار ---
            days_card = MDCard(
                orientation="vertical",
                padding=dp(16),
                spacing=dp(12),
                size_hint_y=None,
                height=dp(240),
                radius=[16],
                elevation=1,
                md_bg_color=CARD_BG
            )

            days_card.add_widget(MDLabel(
                text=fa("روزهای تکرار"),
                font_style="Subtitle2",
                theme_text_color="Custom",
                text_color=DARK_TEXT,
                halign="center",
                font_name="Vazir",
                size_hint_y=None,
                height=dp(26)
            ))

            # (عدد weekday پایتون، نام روز)
            # ترتیب هر ردیف از چپ به راست نوشته شده، پس در نمایش راست‌به‌چپ
            # ردیف‌ها می‌شن: شنبه، یکشنبه، دوشنبه / سه‌شنبه، چهارشنبه، پنج‌شنبه / جمعه
            days = [
                (0, " دوشنبه "),
                (6, "  یکشنبه  "),
                (5, "   شنبه   "),
                (3, "پنج‌شنبه"),
                (2, "چهارشنبه"),
                (1, "سه‌شنبه"),
                (4, "  جمعه  "),
            ]

            # ظرف اصلی وسط‌چین
            days_container = MDBoxLayout(
                orientation="vertical",
                spacing=dp(10),
                size_hint_y=None,
                height=dp(170),
                padding=(dp(10), 0)
            )

            row1 = MDBoxLayout(
                spacing=dp(8),
                size_hint_y=None,
                height=dp(44),
                size_hint_x=None,
                width=dp(265),
                pos_hint={"center_x": 0.5}
            )
            row2 = MDBoxLayout(
                spacing=dp(8),
                size_hint_y=None,
                height=dp(44),
                size_hint_x=None,
                width=dp(265),
                pos_hint={"center_x": 0.5}
            )
            row3 = MDBoxLayout(
                spacing=dp(8),
                size_hint_y=None,
                height=dp(44),
                size_hint_x=None,
                width=dp(75),
                pos_hint={"center_x": 0.5}
            )

            for i, (day_num, day_name) in enumerate(days):
                btn = MDRaisedButton(
                    text=fa(day_name),
                    size_hint=(None, None),
                    size=(dp(100), dp(42)),
                    md_bg_color=GRAY_BTN,
                    text_color=DARK_TEXT,
                    elevation=0,
                    font_name="Vazir",
                    on_release=lambda x, d=day_num: self.toggle_day(d)
                )
                self.day_buttons[day_num] = btn

                if i < 3:
                    row1.add_widget(btn)
                elif i < 6:
                    row2.add_widget(btn)
                else:
                    row3.add_widget(btn)

            days_container.add_widget(row1)
            days_container.add_widget(row2)
            days_container.add_widget(row3)
            days_card.add_widget(days_container)
            content.add_widget(days_card)

            # --- دکمه‌های ذخیره و انصراف ---
            btn_box = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(12),
                size_hint_y=None,
                height=dp(50),
                padding=(0, dp(8), 0, 0)
            )

            save_btn = MDRaisedButton(
                text=fa("ذخیره"),
                md_bg_color=PRIMARY,
                text_color=WHITE,
                font_name="Vazir",
                size_hint_x=0.65,
                elevation=1,
                on_release=self.save
            )
            cancel_btn = MDFlatButton(
                text=fa("انصراف"),
                theme_text_color="Custom",
                text_color=PRIMARY,
                font_name="Vazir",
                size_hint_x=0.35,
                on_release=self.go_back
            )
            btn_box.add_widget(save_btn)
            btn_box.add_widget(cancel_btn)
            content.add_widget(btn_box)

            scroll.add_widget(content)
            root.add_widget(scroll)
            self.add_widget(root)

        def toggle_day(self, day_num):
            btn = self.day_buttons[day_num]
            if getattr(btn, "is_selected", False):
                btn.is_selected = False
                btn.md_bg_color = GRAY_BTN
                btn.text_color = DARK_TEXT
            else:
                btn.is_selected = True
                btn.md_bg_color = PRIMARY
                btn.text_color = WHITE

        def get_selected_days(self):
            return [str(d) for d, btn in self.day_buttons.items() if getattr(btn, "is_selected", False)]

        def on_title_text(self, instance, value):
            if value.strip():
                self.title_preview.text = fa(value)
            else:
                self.title_preview.text = ""

        def on_time_text(self, instance, value):
            digits = "".join(c for c in value if c.isdigit())[:4]
            if len(digits) >= 4:
                formatted = digits[:2] + ":" + digits[2:]
            else:
                formatted = digits
            if formatted != value:
                instance.text = formatted

        def load_for_add(self):
            self.editing_id = None
            self.return_to = "today"
            self.toolbar_title.text = fa("افزودن فعالیت")
            self.title_input.text = ""
            self.title_preview.text = ""
            self.time_input.text = ""
            for btn in self.day_buttons.values():
                btn.is_selected = False
                btn.md_bg_color = GRAY_BTN
                btn.text_color = DARK_TEXT

        def load_for_edit(self, activity_id, return_to="today"):
            self.return_to = return_to
            self.editing_id = activity_id
            act = self.db.get_activity(activity_id)
            if not act:
                return
            self.toolbar_title.text = fa("ویرایش فعالیت")
            self.title_input.text = act["title"]
            self.title_preview.text = fa(act["title"])
            self.time_input.text = act["time"]
            selected_days = [int(d) for d in act["recurrence"].split(",") if d.strip().isdigit()]
            for day_num, btn in self.day_buttons.items():
                if day_num in selected_days:
                    btn.is_selected = True
                    btn.md_bg_color = PRIMARY
                    btn.text_color = WHITE
                else:
                    btn.is_selected = False
                    btn.md_bg_color = GRAY_BTN
                    btn.text_color = DARK_TEXT

        def save(self, *args):
            title = self.title_input.text.strip()
            time = self.time_input.text.strip()

            if not title:
                self.show_error(fa("عنوان فعالیت را وارد کنید"))
                return
                    
            valid_time = False
            if len(time) == 5 and time[2] == ":" and time[:2].isdigit() and time[3:].isdigit():
                hour, minute = int(time[:2]), int(time[3:])
                valid_time = 0 <= hour <= 23 and 0 <= minute <= 59

            if not valid_time:
                self.show_error(fa("ساعت را به فرمت صحیح وارد کنید (مثال: 08:30)"))
                return

            selected = self.get_selected_days()
            if not selected:
                self.show_error(fa("حداقل یک روز را انتخاب کنید"))
                return

            recurrence = ",".join(selected)

            if self.editing_id:
                self.db.update_activity(self.editing_id, title, time, recurrence)
            else:
                self.db.add_activity(title, time, recurrence)

            reminders.schedule_all(self.db)
            self.go_back()


        def show_error(self, text):
            dialog = MDDialog(
                text=text,
                buttons=[MDFlatButton(text=fa("باشه"), on_release=lambda x: dialog.dismiss())]
            )
            dialog.open()

        def go_back(self, *args):
            self.manager.current = self.return_to
