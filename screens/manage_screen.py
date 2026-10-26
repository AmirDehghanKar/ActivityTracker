from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.metrics import dp
from datetime import date
from persian import fa
import reminders

PRIMARY = (0.0, 0.208, 0.400, 1)
SECONDARY = (1.0, 0.765, 0.0, 1)
WHITE = (1, 1, 1, 1)
DARK_TEXT = (0.12, 0.12, 0.12, 1)
LIGHT_BG = (0.96, 0.97, 0.98, 1)
CARD_BG = (1, 1, 1, 1)
GRAY_BTN = (0.88, 0.90, 0.93, 1)
RED = (0.85, 0.25, 0.25, 1)

# عدد weekday پایتون -> نام روز
DAY_NAMES = {
    5: "شنبه", 6: "یکشنبه", 0: "دوشنبه", 1: "سه‌شنبه",
    2: "چهارشنبه", 3: "پنج‌شنبه", 4: "جمعه",
}
# ردیف‌ها از راست به چپ خوانده می‌شن
ROW1 = [5, 6, 0, 1]     # شنبه تا سه‌شنبه
ROW2 = [2, 3, 4]        # چهارشنبه تا جمعه


class ManageScreen(MDScreen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.selected_day = date.today().weekday()
        self.day_buttons = {}
        self.build_ui()

    def build_ui(self):
        root = MDBoxLayout(orientation="vertical", md_bg_color=LIGHT_BG)

        # ========== هدر (مثل بقیه صفحات) ==========
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
        header.add_widget(MDLabel(
            text=fa("مدیریت فعالیت"),
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=WHITE,
            halign="right",
            valign="middle",
            size_hint_x=1,
            font_name="Vazir",
            bold=True
        ))
        header.add_widget(MDLabel(size_hint=(None, None), size=(dp(80), dp(36))))
        root.add_widget(header)

        # ========== انتخاب روز ==========
        day_box = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(110),
            padding=(dp(12), dp(10), dp(12), dp(4)),
            spacing=dp(8)
        )
        day_box.add_widget(self._make_day_row(ROW1, pad_left=False))
        day_box.add_widget(self._make_day_row(ROW2, pad_left=True))
        root.add_widget(day_box)

        # عنوان لیست
        self.list_title = MDLabel(
            text="",
            font_name="Vazir",
            theme_text_color="Custom",
            text_color=PRIMARY,
            halign="right",
            bold=True,
            size_hint_y=None,
            height=dp(30),
            padding=(dp(16), 0)
        )
        root.add_widget(self.list_title)

        # ========== لیست فعالیت‌ها ==========
        scroll = ScrollView(do_scroll_x=False)
        self.list_box = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(8),
            padding=(dp(12), dp(4), dp(12), dp(16))
        )
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll.add_widget(self.list_box)
        root.add_widget(scroll)

        self.add_widget(root)

    def _make_day_row(self, day_nums, pad_left):
        row = MDBoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))
        # چون چیدمان چپ به راسته، برای نمایش راست‌به‌چپ ترتیب رو برعکس اضافه می‌کنیم
        if pad_left:
            row.add_widget(Widget())   # جای خالی ستون چهارم، سمت چپ
        for d in reversed(day_nums):
            btn = MDRaisedButton(
                text=fa(DAY_NAMES[d]),
                font_name="Vazir",
                font_size="12sp",
                size_hint=(1, 1),
                elevation=0,
                md_bg_color=GRAY_BTN,
                text_color=DARK_TEXT,
                on_release=lambda x, day=d: self.select_day(day)
            )
            self.day_buttons[d] = btn
            row.add_widget(btn)
        return row

    # ---------- رویدادها ----------
    def on_enter(self, *args):
        self.refresh()

    def select_day(self, day):
        self.selected_day = day
        self.refresh()

    def refresh(self):
        for d, btn in self.day_buttons.items():
            if d == self.selected_day:
                btn.md_bg_color = PRIMARY
                btn.text_color = WHITE
            else:
                btn.md_bg_color = GRAY_BTN
                btn.text_color = DARK_TEXT

        acts = []
        for a in self.db.get_all_activities():
            days = [int(x) for x in str(a["recurrence"]).split(",") if x.strip().isdigit()]
            if self.selected_day in days:
                acts.append(a)
        acts.sort(key=lambda a: a["time"])

        self.list_title.text = fa(
            f"فعالیت‌های {DAY_NAMES[self.selected_day]} ({len(acts)})"
        )

        self.list_box.clear_widgets()
        if not acts:
            self.list_box.add_widget(MDLabel(
                text=fa("برای این روز فعالیتی تعریف نشده"),
                halign="center",
                theme_text_color="Hint",
                font_name="Vazir",
                size_hint_y=None,
                height=dp(90)
            ))
            return

        for act in acts:
            self.list_box.add_widget(self._make_row(act))

    def _make_row(self, act):
        card = MDCard(
            size_hint_y=None,
            height=dp(60),
            padding=(dp(8), dp(8)),
            radius=[14],
            elevation=0,
            md_bg_color=CARD_BG,
            line_color=(0.88, 0.90, 0.92, 1),
            line_width=1
        )
        row = MDBoxLayout(orientation="horizontal", spacing=dp(6))

        del_btn = MDFlatButton(
            text=fa("حذف"),
            theme_text_color="Custom",
            text_color=RED,
            font_name="Vazir",
            size_hint=(None, None),
            size=(dp(56), dp(36)),
            pos_hint={"center_y": 0.5},
            line_color=RED,
            line_width=1,
            on_release=lambda x, a_id=act["id"], t=act["title"]: self.confirm_delete(a_id, t)
        )
        edit_btn = MDFlatButton(
            text=fa("ویرایش"),
            theme_text_color="Custom",
            text_color=PRIMARY,
            font_name="Vazir",
            size_hint=(None, None),
            size=(dp(68), dp(36)),
            pos_hint={"center_y": 0.5},
            line_color=PRIMARY,
            line_width=1,
            on_release=lambda x, a_id=act["id"]: self.go_to_edit(a_id)
        )
        title_lbl = MDLabel(
            text=fa(act["title"]),
            font_name="Vazir",
            halign="right",
            valign="middle",
            shorten=True,
            shorten_from="right",
            theme_text_color="Custom",
            text_color=DARK_TEXT,
            size_hint_x=1
        )
        title_lbl.bind(size=lambda inst, s: setattr(inst, "text_size", s))

        time_lbl = MDLabel(
            text=act["time"],
            font_name="Vazir",
            halign="right",
            valign="middle",
            bold=True,
            theme_text_color="Custom",
            text_color=PRIMARY,
            size_hint_x=None,
            width=dp(52)
        )

        # از چپ به راست: حذف، ویرایش، عنوان، ساعت
        row.add_widget(del_btn)
        row.add_widget(edit_btn)
        row.add_widget(title_lbl)
        row.add_widget(time_lbl)
        card.add_widget(row)
        return card

    # ---------- ویرایش و حذف ----------
    def go_to_edit(self, activity_id):
        self.manager.current = "add_edit"
        self.manager.get_screen("add_edit").load_for_edit(activity_id, return_to="manage")

    def confirm_delete(self, activity_id, title):
        self.delete_dialog = MDDialog(
            text=fa(f"فعالیت «{title}» حذف شود؟"),
            buttons=[
                MDFlatButton(
                    text=fa("انصراف"),
                    theme_text_color="Custom",
                    text_color=PRIMARY,
                    font_name="Vazir",
                    on_release=lambda x: self.delete_dialog.dismiss()
                ),
                MDRaisedButton(
                    text=fa("حذف"),
                    md_bg_color=RED,
                    text_color=WHITE,
                    font_name="Vazir",
                    on_release=lambda x: self.do_delete(activity_id)
                ),
            ]
        )
        self.delete_dialog.open()

    def do_delete(self, activity_id):
        self.delete_dialog.dismiss()
        self.db.delete_activity(activity_id)
        self.db.recalculate_day_status(date.today())
        reminders.schedule_all(self.db)
        self.refresh()

    def go_back(self, *args):
        self.manager.current = "today"