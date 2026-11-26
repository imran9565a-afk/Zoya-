#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "=== MAYA Termux Setup ==="
pkg update -y
pkg upgrade -y
pkg install -y git python clang make cmake zip unzip wget curl openjdk-17

if [ -d "$HOME/MAYA" ]; then
  cd "$HOME/MAYA"
  git pull --ff-only
elif [ -d "$HOME/Maya-" ]; then
  cd "$HOME/Maya-"
  git pull --ff-only
else
  git clone https://github.com/imran9565a-afk/Maya-.git "$HOME/MAYA"
  cd "$HOME/MAYA"
fi

echo "=== Python syntax check ==="
python -m py_compile main.py
echo
echo "MAYA source is ready in: $PWD"
echo "Note: the Android GUI APK is built by GitHub Actions, not by running Kivy inside Termux."
echo "Open: https://github.com/imran9565a-afk/Maya-/actions"
