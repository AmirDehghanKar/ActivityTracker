from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path
from datetime import date, timedelta
import os
import reminders
from kivymd.uix.label import MDLabel
from screens.today_screen import TodayScreen
from screens.add_edit_screen import AddEditScreen
from screens.reports_screen import ReportsScreen
from screens.profile_screen import ProfileScreen
from database import Database
from screens.manage_screen import ManageScreen
from kivy.core.window import Window
from kivy.utils import platform

Window.softinput_mode = "below_target"

# ثبت فونت
FONT_PATH = os.path.join(os.path.dirname(__file__), "Vazirmatn.ttf")
resource_add_path(os.path.dirname(__file__))
LabelBase.register(name="Vazir", fn_regular=FONT_PATH)


class SplashScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "splash"
        self.md_bg_color = (0, 0, 0, 1)   # هم‌رنگ حاشیه عکس

        splash_path = os.path.join(os.path.dirname(__file__), "splash.png")
        if os.path.exists(splash_path):
            self.add_widget(Image(
                source=splash_path,
                fit_mode="cover",        # کل صفحه را پر می‌کند
                size_hint=(1, 1),
                pos_hint={"x": 0, "y": 0}
            ))
        else:
            self.add_widget(MDLabel(
                text="ZISTRO",
                halign="center",
                theme_text_color="Custom",
                text_color=(1.0, 0.765, 0.0, 1),
                font_style="H3",
                bold=True
            ))


class ActivityTrackerApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # مسیر امن ذخیره داده (روی اندروید: پوشه خصوصی برنامه)
        os.makedirs(self.user_data_dir, exist_ok=True)
        db_path = os.path.join(self.user_data_dir, "activity_tracker.db")
        self.db = Database(db_path)

        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # اعمال فونت به همه استایل‌ها
        for style in self.theme_cls.font_styles:
            self.theme_cls.font_styles[style][0] = "Vazir"

    def build(self):
        self.title = "ZISTRO"

        self.sm = MDScreenManager()

        self.sm.add_widget(SplashScreen())
        self.sm.add_widget(TodayScreen(name="today", db=self.db))
        self.sm.add_widget(AddEditScreen(name="add_edit", db=self.db))
        self.sm.add_widget(ReportsScreen(name="reports", db=self.db))
        self.sm.add_widget(ProfileScreen(name="profile", db=self.db))
        self.sm.add_widget(ManageScreen(name="manage", db=self.db))
        self.sm.current = "splash"

        # نوارهای فضای امن: بالا هم‌رنگ هدر، پایین سفید
        self.top_pad = MDBoxLayout(
            size_hint_y=None, height=0,
            md_bg_color=(0.0, 0.208, 0.400, 1)
        )
        self.bottom_pad = MDBoxLayout(
            size_hint_y=None, height=0,
            md_bg_color=(1, 1, 1, 1)
        )

        root = MDBoxLayout(orientation="vertical")
        root.add_widget(self.top_pad)
        root.add_widget(self.sm)
        root.add_widget(self.bottom_pad)

        Clock.schedule_once(self.go_to_main, 5)
        return root
        # بعد از ۵ ثانیه برو به صفحه اصلی و اسپلش را حذف کن
        Clock.schedule_once(self.go_to_main, 5)

        return self.sm

    def go_to_main(self, *args):
        # فضای امن بعد از اسپلش اعمال می‌شود تا اسپلش تمام‌صفحه بماند
        top, bottom = self._get_insets()
        self.top_pad.height = top
        self.bottom_pad.height = bottom

        self.sm.current = "today"
        Clock.schedule_once(self._remove_splash, 1)

    def _remove_splash(self, *args):
        if self.sm.has_screen("splash"):
            self.sm.remove_widget(self.sm.get_screen("splash"))

    def on_start(self):
        reminders.request_permission()
        reminders.schedule_all(self.db)
        self.db.purge_status_before_first_activity()
        Clock.schedule_once(lambda dt: self.check_past_days(), 0.5)

    def check_past_days(self):
        today = date.today()
        for i in range(1, 40):
            d = today - timedelta(days=i)
            self.db.recalculate_day_status(d)
            
    def _get_insets(self):
        """ارتفاع نوار وضعیت (بالا) و نوار ناوبری (پایین) به پیکسل"""
        if platform != "android":
            return 0, 0
        top = bottom = 0
        try:
            from jnius import autoclass
            activity = autoclass("org.kivy.android.PythonActivity").mActivity
            insets = activity.getWindow().getDecorView().getRootWindowInsets()
            if insets is not None:
                top = insets.getSystemWindowInsetTop()
                bottom = insets.getSystemWindowInsetBottom()
            if top == 0:
                res = activity.getResources()
                rid = res.getIdentifier("status_bar_height", "dimen", "android")
                if rid > 0:
                    top = res.getDimensionPixelSize(rid)
        except Exception as e:
            print("insets error:", e)
        return top, bottom
        
    def on_stop(self):
        self.db.close()


if __name__ == "__main__":
    ActivityTrackerApp().run()
