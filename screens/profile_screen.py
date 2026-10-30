from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.floatlayout import FloatLayout
from kivy.metrics import dp
from kivy.uix.widget import Widget
from persian import fa
import webbrowser
import os
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
import reminders
from kivymd.uix.dialog import MDDialog

# رنگ‌های اصلی (همان today_screen)
PRIMARY = (0.0, 0.208, 0.400, 1)       # #003566
SECONDARY = (1.0, 0.765, 0.0, 1)       # #ffc300
WHITE = (1, 1, 1, 1)
DARK_TEXT = (0.12, 0.12, 0.12, 1)
LIGHT_BG = (0.96, 0.97, 0.98, 1)
CARD_BG = (1, 1, 1, 1)


class ProfileScreen(MDScreen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.build_ui()

    def build_ui(self):
        root = MDBoxLayout(orientation="vertical", md_bg_color=LIGHT_BG)

        # ========== هدر ==========
        header = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(78),
            md_bg_color=PRIMARY,
            padding=(dp(16), dp(17), dp(16), dp(17)),
            spacing=dp(16)
        )

        top_row = MDBoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))

        # دکمه بازگشت با بردر سفید
        back_btn = MDFlatButton(
            text=fa("بازگشت"),
            theme_text_color="Custom",
            text_color=WHITE,
            font_name="Vazir",
            size_hint=(None, None),
            size=(dp(80), dp(34)),
            line_color=WHITE,
            line_width=1,
            on_release=self.go_back
        )
        top_row.add_widget(back_btn)

        # عنوان وسط‌چین
        title = MDLabel(
            text=fa("پروفایل"),
            font_style="H5",
            theme_text_color="Custom",
            text_color=WHITE,
            halign="right",
            valign="middle",
            size_hint_x=1,
            font_name="Vazir",
            bold=True
        )
        top_row.add_widget(title)

        # فضای خالی برای تعادل بصری
        top_row.add_widget(MDLabel(size_hint=(None, None), size=(dp(80), dp(34))))

        header.add_widget(top_row)

        # # زیر‌عنوان
        # subtitle = MDLabel(
        #     text=fa("تنظیمات نام کاربری"),
        #     theme_text_color="Custom",
        #     text_color=(1, 1, 1, 0.7),
        #     halign="center",
        #     font_name="Vazir",
        #     font_style="Caption",
        #     size_hint_y=None,
        #     height=dp(22)
        # )
        # header.add_widget(subtitle)
        root.add_widget(header)

        # ========== محتوای اصلی (اسکرول‌پذیر) ==========
        scroll = ScrollView(do_scroll_x=False)
        content = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=(dp(16), dp(16), dp(16), dp(16)),
            spacing=dp(14)
        )
        content.bind(minimum_height=content.setter("height"))
        scroll.add_widget(content)

        # کارت نام
        card = MDCard(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(12),
            size_hint_y=None,
            height=dp(190),
            radius=[18],
            elevation=1,
            md_bg_color=CARD_BG
        )

        card.add_widget(MDLabel(
            text=fa("نام شما"),
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=DARK_TEXT,
            halign="right",
            font_name="Vazir",
            size_hint_y=None,
            height=dp(35)
        ))

        # فیلد نام با پیش‌نمایش فارسی
        name_box = FloatLayout(size_hint_y=None, height=dp(52))

        self.name_input = MDTextField(
            mode="rectangle",
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0},
            font_name="Vazir",
            multiline=False,
            line_color_normal=PRIMARY,
            line_color_focus=PRIMARY,
        )
        self.name_input.foreground_color = (1, 1, 1, 0)
        self.name_input.text_color_normal = (1, 1, 1, 0)
        self.name_input.text_color_focus = (1, 1, 1, 0)
        self.name_input.bind(text=self.on_name_text)
        name_box.add_widget(self.name_input)

        self.name_preview = MDLabel(
            text="",
            font_name="Vazir",
            font_style="Body1",
            halign="right",
            valign="center",
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0},
            padding=(dp(14), 0, dp(14), 0),
            theme_text_color="Custom",
            text_color=DARK_TEXT
        )
        name_box.add_widget(self.name_preview)
        card.add_widget(name_box)

        # دکمه ذخیره
        save_btn = MDRaisedButton(
            text=fa("ذخیره نام"),
            md_bg_color=PRIMARY,
            text_color=WHITE,
            font_name="Vazir",
            size_hint_x=1,
            elevation=1,
            on_release=self.save_name
        )
        card.add_widget(save_btn)

        content.add_widget(card)

        info_card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(6),
            size_hint_y=None,
            height=dp(90),          # قبلاً 100 بود
            radius=[16],
            elevation=0,
            md_bg_color=(0.0, 0.208, 0.400, 0.06)
        )

        info_card.add_widget(MDLabel(
            text=fa("نکته:"),
            font_style="Subtitle2",
            theme_text_color="Custom",
            text_color=PRIMARY,
            halign="right",
            font_name="Vazir",
            size_hint_y=None,
            height=dp(20)
        ))

        info_card.add_widget(MDLabel(
            text=fa("این نام فقط در بخش گزارش‌ها نمایش داده می‌شود."),
            font_style="Caption",
            font_size="9sp",
            theme_text_color="Custom",
            text_color=(0.35, 0.38, 0.42, 1),
            halign="right",
            font_name="Vazir",
            size_hint_y=None,
            height=dp(30)
        ))

        content.add_widget(info_card)

        contact_card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(130),
            radius=[16],
            elevation=1,
            md_bg_color=CARD_BG
        )

        contact_card.add_widget(MDLabel(
            text=fa("ارتباط با طراح و توسعه‌دهنده:"),
            font_style="Subtitle2",
            theme_text_color="Custom",
            text_color=PRIMARY,
            halign="right",
            font_name="Vazir",
            size_hint_y=None,
            height=dp(24)
        ))

        buttons_row = MDBoxLayout(
            size_hint_y=None,
            height=dp(56),
            spacing=dp(10)
        )
        buttons_row.add_widget(self._make_social_btn(
            label="Telegram",
            handle="@Poseidon_8",
            url="https://t.me/Poseidon_8",
            icon_file="telegram.png"
        ))
        buttons_row.add_widget(self._make_social_btn(
            label="Instagram",
            handle="@_amir.dk_",
            url="https://instagram.com/_amir.dk_",
            icon_file="instagram.png"
        ))
        contact_card.add_widget(buttons_row)

        content.add_widget(contact_card)

        content.add_widget(Widget())

        root.add_widget(scroll)

        # ========== فوتر (ثابت، پایین صفحه) ==========
        footer = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(64),
            spacing=dp(2),
            padding=(0, dp(8), 0, dp(8))
        )

        footer.add_widget(MDLabel(
            text="Developed by: A.DehghanKar",
            font_name="Vazir",
            theme_text_color="Custom",
            text_color=(0.45, 0.48, 0.52, 1),
            halign="center",
            size_hint_y=None,
            height=dp(22)
        ))

        footer.add_widget(MDLabel(
            text="Version: 1.0.4",
            font_name="Vazir",
            theme_text_color="Custom",
            text_color=(0.55, 0.58, 0.62, 1),
            halign="center",
            size_hint_y=None,
            height=dp(20)
        ))

        root.add_widget(footer)
        self.add_widget(root)

    def _make_social_btn(self, label, handle, url, icon_file):
        card = MDCard(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(56),
            padding=(dp(10), dp(8)),
            spacing=dp(8),
            radius=[14],
            elevation=0,
            md_bg_color=(1, 1, 1, 1),
            line_color=(0.88, 0.90, 0.93, 1),
            line_width=1,
            ripple_behavior=True,
            on_release=lambda x: self.open_link(url)
        )

        # لوگوی واقعی
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        card.add_widget(Image(
            source=os.path.join(root_dir, icon_file),
            size_hint=(None, None),
            size=(dp(36), dp(36)),
            pos_hint={"center_y": 0.5},
            fit_mode="contain"
        ))

        # نام برند و ID
        text_box = MDBoxLayout(orientation="vertical", spacing=dp(0))
        name_lbl = MDLabel(
            text=label,
            halign="left",
            valign="bottom",
            theme_text_color="Custom",
            text_color=DARK_TEXT,
            bold=True,
            font_style="Caption",
            font_name="Vazir"
        )
        handle_lbl = MDLabel(
            text=handle,
            halign="left",
            valign="top",
            theme_text_color="Custom",
            text_color=(0.45, 0.48, 0.52, 1),
            font_style="Caption",
            font_name="Vazir",
            shorten=True,
            shorten_from="right"
        )
        for l in (name_lbl, handle_lbl):
            l.bind(size=lambda inst, s: setattr(inst, "text_size", s))
        text_box.add_widget(name_lbl)
        text_box.add_widget(handle_lbl)
        card.add_widget(text_box)
        return card
    
    def open_link(self, url):
        try:
            from kivy.utils import platform
            if platform == "android":
                from jnius import autoclass
                Intent = autoclass("android.content.Intent")
                Uri = autoclass("android.net.Uri")
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                PythonActivity.mActivity.startActivity(intent)
            else:
                webbrowser.open(url)
        except Exception as e:
            print("open_link error:", e)

    def on_name_text(self, instance, value):
        if value.strip():
            self.name_preview.text = fa(value)
        else:
            self.name_preview.text = ""

    def on_enter(self, *args):
        current_name = self.db.get_name()
        self.name_input.text = current_name
        self.name_preview.text = fa(current_name) if current_name else ""

    def save_name(self, *args):
        name = self.name_input.text.strip()
        if name:
            self.db.set_name(name)
            self.name_preview.text = fa(name)
            reminders.schedule_all(self.db)
            self.show_message("نام کاربری شما با موفقیت ثبت شد.")
        else:
            self.show_message("لطفاً نام خود را وارد کنید.")

    def show_message(self, text):
        dialog = MDDialog(
            text=fa(text),
            buttons=[
                MDFlatButton(
                    text=fa("باشه"),
                    theme_text_color="Custom",
                    text_color=PRIMARY,
                    font_name="Vazir",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

    def go_back(self, *args):
        self.manager.current = "today"
