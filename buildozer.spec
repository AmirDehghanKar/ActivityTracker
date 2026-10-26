[app]

# نام نمایشی اپ
title = ZISTRO

# نام پکیج (باید یکتا باشد)
package.name = zistro

# دامنه پکیج
package.domain = org.zistro

# فایل اصلی اجرا
source.dir = .
source.include_exts = py,png,jpg,jpeg,gif,ttf,kv,atlas,json,txt

# نسخه اپ
version = 1.0.2

# نیازمندی‌ها
requirements = hostpython3==3.11.6,python3==3.11.6,kivy==2.3.1,kivymd==1.2.0,pillow,sqlite3,arabic-reshaper,python-bidi==0.4.2,jdatetime,six
source.exclude_dirs = .github,bin,.buildozer,__pycache__

# جهت صفحه
orientation = portrait

# آیکون اپ اندروید
icon.filename = %(source.dir)s/icon.png

# اسپلش (اختیاری)
presplash.filename = %(source.dir)s/splash.png
android.presplash_color = #000000

# تمام صفحه
fullscreen = 0

# مجوزها (برای نوتیفیکیشن آینده)
android.permissions = INTERNET,VIBRATE,RECEIVE_BOOT_COMPLETED,POST_NOTIFICATIONS,SCHEDULE_EXACT_ALARM,USE_EXACT_ALARM

android.add_src = java
#android.extra_manifest_application_arguments = extra_manifest_application.xml

# حداقل نسخه اندروید
android.minapi = 24


# API
android.api = 35
android.archs = arm64-v8a


# قبول لایسنس
android.accept_sdk_license = True

[buildozer]

log_level = 2
warn_on_root = 1
