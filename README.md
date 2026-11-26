# Maya — Android AI Assistant

Maya is an Android assistant built with Python/Kivy and GitHub Actions. It uses the Google Gemini API for multilingual AI answers.

## Included features

- Gemini-powered Hindi and English question answering
- Recent conversation context while the app remains open
- Image attachment and image-question requests
- Safe arithmetic calculator
- Android text-to-speech replies and Android speech-recognition input (device/service dependent)
- Battery, vibration, flashlight and user-triggered calling where Android permissions and device support allow
- Google, YouTube and Instagram shortcuts
- To-do list, alarm, password-lock screen and Instagram hashtag/bio helper
- GitHub Actions debug APK build

## Build the APK

1. Open the [GitHub Actions page](https://github.com/imran9565a-afk/Zoya-/actions).
2. Select **Build Maya Android APK** and choose **Run workflow**, or push a commit to `main`.
3. Open the newest successful run and download the `maya-debug-apk` artifact.
4. Extract the ZIP and install the APK on Android.

## Connect Gemini

1. Create an API key in [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Install and open Maya.
3. Open **Gemini / Google Search Settings** and enter your key.
4. Keep the key private. It is saved in Maya's private app data and is not committed to this repository.

An API key stored in an APK/device is not a server-grade secret. Do not distribute an APK with your key prefilled. For a public multi-user service, use a secured backend proxy.

## Termux source setup

```bash
pkg update -y && pkg upgrade -y
pkg install -y git
git clone https://github.com/imran9565a-afk/Zoya-.git "$HOME/MAYA"
cd "$HOME/MAYA"
bash termux_setup.sh
```

If already cloned:

```bash
cd "$HOME/MAYA"
git pull --ff-only
python -m py_compile main.py
```

Termux downloads and checks source code. GitHub Actions builds the Android APK; the full Kivy Android build toolchain is not run locally in Termux.

## Important limitations

- Maya is an AI assistant client, not a copy of ChatGPT or its proprietary app/model.
- AI replies require internet access and a valid Gemini API key. Model availability, quotas and charges depend on Google and the selected account.
- Voice recognition and spoken replies depend on Android speech/TTS services and device support. Continuous wake-word listening and full-duplex live voice are not yet implemented.
- Background wake-word listening, persistent cloud chat sync, unrestricted phone control and server-side multi-user key protection are not included.
- Phone actions require user interaction and Android permissions.

## Main files

- `main.py` — Maya Kivy app, Gemini chat, image requests, utilities and speech support
- `buildozer.spec` — Android package settings and permissions
- `.github/workflows/build.yml` — GitHub Actions APK build
- `termux_setup.sh` — Termux install/source-check helper
