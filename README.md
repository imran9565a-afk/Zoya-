# ZOYA AI — Android Assistant

ZOYA is an Android assistant app built with Kivy and GitHub Actions. This project now connects to Google's Gemini API and can use Gemini's Google Search grounding for current web answers.

## Included in this build

- Gemini AI chat using the Google Gemini API (model: `gemini-3.8-flash`)
- Google Search grounding enabled for answers that need current web information; source links are shown when returned by the API
- Short conversation context (recent turns) while the app remains open
- Hindi and English responses
- Safe arithmetic calculator
- Phone utilities already present in the project: battery status, vibration, flashlight and a user-triggered phone call (device/permission dependent)
- Google, YouTube and Instagram shortcuts
- ZOYA app icon artwork in `assets/zoya_ai.svg`
- GitHub Actions workflow to build a debug APK

## First-time setup

1. Create a Gemini API key in [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Open ZOYA on your Android phone.
3. Tap **GEMINI / GOOGLE SEARCH SETTINGS**.
4. Paste your own API key and tap **SAVE & CONNECT**.
5. Ask a question. Google Search grounding is enabled in each Gemini request.

The key is stored in the app's private Android data directory, not committed into this repository. Do not share your key or publish an APK containing someone else's key. For a public app with multiple users, move API calls behind a secured backend rather than distributing one shared key inside an APK.

## Build APK from an Android phone

1. Open this repository on GitHub.
2. Go to **Actions** and enable workflows if GitHub asks.
3. Open **Build ZOYA Android APK**. A push to `main` also starts the workflow.
4. Wait for the workflow to finish successfully.
5. Open the successful run, scroll to **Artifacts**, and download `zoya-debug-apk`.
6. Extract the ZIP and install the APK. Android may ask permission to install apps from your browser/file manager.

## Phone access and privacy

ZOYA does not get unrestricted access to the phone. Android controls access through permissions and user actions. The current app only attempts the listed utilities; calls require a user-entered number and supported call permission. It does not silently read all photos, messages, contacts, files, microphone recordings or other private data.

## Important limitations

- This is a Gemini-powered assistant app, not a copy of ChatGPT or Gemini's proprietary apps. Model capability, uptime, context limits, and available features depend on Google's API.
- A Gemini API key and internet connection are required for AI answers.
- Google Search grounding and Gemini API usage are subject to Google's current quotas, availability, and pricing. Check Google AI Studio before heavy use.
- API keys stored on a phone are private to the app sandbox but are not a secure server-side secret. Do not distribute a shared key in a public APK.
- The app currently has text chat; voice recognition, image generation, photo editing, file-reading, contact access and background wake-word listening are not implemented.
- The in-app alarm only runs while the app process remains alive.
- The to-do list is temporary and resets when the app restarts.
- Phone utilities vary by Android version, hardware, and permissions.

## Main files

- `main.py`: Kivy app and Gemini/Google Search integration
- `buildozer.spec`: Android build configuration
- `.github/workflows/build.yml`: GitHub Actions APK build workflow
- `assets/zoya_ai.svg`: ZOYA icon artwork
