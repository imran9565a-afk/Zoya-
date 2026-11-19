# ZOYA — Android AI Assistant

ZOYA is an Android assistant project built with Python/Kivy and GitHub Actions. It uses the Google Gemini API for AI answers.

## Current features

- Gemini-powered Hindi and English question answering
- Recent-turn conversation context while the app remains open
- Google Search grounding for supported current-information requests
- Photo attachment and image-question requests (subject to the selected model/API access)
- Safe arithmetic calculator
- Spoken replies through the available Android text-to-speech service
- Voice-input button using the platform speech-recognition bridge when supported; otherwise use the Android keyboard microphone
- Phone utilities such as battery, vibration, flashlight and user-triggered calling where Android permissions and device support allow
- Google, YouTube and Instagram shortcuts
- GitHub Actions debug APK build

## Setup from Termux (Android phone)

Install Termux from a trusted source, open it, then run:

```bash
pkg update -y && pkg upgrade -y
pkg install -y git
git clone https://github.com/imran9565a-afk/Zoya-.git "$HOME/ZOYA"
cd "$HOME/ZOYA"
bash termux_setup.sh
```

If the repository is already cloned, run:

```bash
cd "$HOME/ZOYA"
git pull --ff-only
python -m py_compile main.py
```

Termux is used to download and check the source. The Kivy Android GUI is packaged as an APK by GitHub Actions; running the APK build toolchain locally in Termux is not the supported build path.

## Connect Gemini

1. Create your own API key at https://aistudio.google.com/app/apikey.
2. Install and open ZOYA.
3. Open Gemini settings and enter your key.
4. Keep the key private. It is saved in the app's private data directory and is not committed to this repository.

API keys stored in an APK/device are not server-grade secrets. Do not put a shared key in source code or distribute an APK with your key prefilled. For a public multi-user service, use a secured backend proxy.

## Build the APK

1. Open https://github.com/imran9565a-afk/Zoya-/actions
2. Select **Build ZOYA Android APK**.
3. If GitHub asks, enable Actions.
4. Open the newest run and wait for it to finish successfully.
5. Download the `zoya-debug-apk` artifact, extract the ZIP, and install the APK.

A push to `main` also starts the workflow automatically.

## Important limits

- ZOYA is a ChatGPT-style assistant client, not a copy of ChatGPT or its proprietary model/app.
- AI answers require internet access and a working Gemini API key; model access, quotas and charges depend on Google.
- Voice recognition availability depends on the Android speech service/device. If it does not return text, use the keyboard microphone; voice reply uses Android TTS when available.
- Image generation, persistent cloud chat sync, background wake-word listening, full file reading, and unrestricted phone control are not included.
- Phone actions require user interaction and Android permissions. ZOYA does not silently access private phone data.

## Main files

- `main.py` — Kivy app, Gemini chat, image requests, utilities and speech output
- `buildozer.spec` — Android package and permissions
- `.github/workflows/build.yml` — GitHub Actions APK build
- `termux_setup.sh` — Termux install/source-check helper
