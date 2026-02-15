[app]
title = JETSTAR POS
package.name = jetstarpos
package.domain = com.jetstar

source.dir = .
source.include_exts = py
source.main = jetstar_pos_mobile.py

version = 1.0
requirements = python3,kivy

orientation = landscape
fullscreen = 0

# App icon (add icon.png to root folder if you have one)
# icon.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 2
warn_on_root = 1

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31

android.accept_sdk_license = True
android.arch = armeabi-v7a

p4a.branch = master
