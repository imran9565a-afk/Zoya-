[app]
title = ZOYA AI Assistant
package.name = zoyaassistant
package.domain = com.imran.zoya
source.dir = .
source.include_exts = py,kv,png,jpg,atlas,json,txt,svg
version = 2.0.0
requirements = python3,kivy==2.1.0,plyer
orientation = portrait
fullscreen = 0
icon.filename = assets/zoya_ai.png
android.permissions = INTERNET,CALL_PHONE,VIBRATE,CAMERA
android.api = 35
android.minapi = 23
android.ndk = 27c
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
p4a.bootstrap = sdl2
p4a.branch = v2024.01.21
android.allow_backup = False
[buildozer]
log_level = 2
warn_on_root = 1
