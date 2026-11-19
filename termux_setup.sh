#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "=== ZOYA Termux Setup ==="
pkg update -y
pkg upgrade -y
pkg install -y git python clang make cmake zip unzip wget curl openjdk-17

if [ -d "$HOME/ZOYA" ]; then
  cd "$HOME/ZOYA"
  git pull --ff-only
elif [ -d "$HOME/Zoya-" ]; then
  cd "$HOME/Zoya-"
  git pull --ff-only
else
  git clone https://github.com/imran9565a-afk/Zoya-.git "$HOME/ZOYA"
  cd "$HOME/ZOYA"
fi

echo "=== Python syntax check ==="
python -m py_compile main.py
echo
echo "ZOYA source is ready in: $PWD"
echo "Note: the Android GUI APK is built by GitHub Actions, not by running Kivy inside Termux."
echo "Open: https://github.com/imran9565a-afk/Zoya-/actions"
