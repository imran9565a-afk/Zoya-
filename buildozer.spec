[app]
title = MAYA
package.name = mayaassistant
package.domain = com.imran.maya
source.dir = .
source.include_exts = py,kv,png,jpg,atlas,json,txt,svg
version = 3.0.0
requirements = python3,kivy==2.1.0,plyer
orientation = portrait
fullscreen = 0
icon.filename = assets/maya_ai.png
android.permissions = INTERNET,RECORD_AUDIO,MODIFY_AUDIO_SETTINGS,CALL_PHONE,VIBRATE,CAMERA
android.api = 35
android.minapi = 23
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
p4a.bootstrap = sdl2
p4a.branch = v2024.01.21
android.allow_backup = False
[buildozer]
log_level = 2
warn_on_root = 1
