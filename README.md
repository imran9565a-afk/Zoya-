# ZOYA Smart Assistant (Kivy)

Android-friendly Kivy project designed to build with GitHub Actions.

## Features
- Safe arithmetic calculator with AST allow-list and result limits
- DuckDuckGo Instant Answer lookup (internet required; not a full generative AI chatbot)
- Website shortcuts, Instagram hashtag/bio helper
- Optional Plyer battery, vibration, torch and call actions (device/permission dependent)
- In-app alarm and temporary to-do list
- Basic password check popup

## Build APK on GitHub from an Android phone
1. Open this repository on GitHub.
2. Go to **Actions** and enable workflows if GitHub asks.
3. Open **Build ZOYA Android APK** and tap **Run workflow**, or push a commit to `main`.
4. Wait until the run is green.
5. Open the successful run, scroll to **Artifacts**, and download `zoya-debug-apk`.
6. Extract the ZIP and install the APK. Android may ask permission to install apps from your browser/file manager.

## Important limitations
- The alarm is in-app only. It will not reliably fire if Android kills the app or the phone restarts.
- To-do items are held in memory and are not saved after closing the app.
- Voice recognition is not implemented in this build.
- The password popup is not device-grade security; change the sample password in `main.py` before building.
- Calls, torch, battery and vibration vary by device, Android version and permissions.
- Network answers are limited to DuckDuckGo Instant Answer data. No AI API key is included.

## Build files
- `main.py`: application entry point
- `buildozer.spec`: Buildozer configuration
- `.github/workflows/build.yml`: GitHub Actions APK build
