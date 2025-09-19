#!/bin/bash
set -e

DESKTOP="$HOME/Desktop"

echo "[1/4] Update system"
sudo apt update && sudo apt upgrade -y

echo "[2/4] Install dependencies"
sudo apt install -y python3-pyqt6 python3-opencv python3-gpiozero python3-picamera2 git

echo "[3/4] Install Python packages"
pip3 install --upgrade pip
pip3 install -r requirements.txt

echo "[4/4] Copy project to Desktop"
rm -rf "$DESKTOP/run"
cp -r run "$DESKTOP/"

# สร้าง autostart .desktop file
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/omicuv.desktop <<EOF
[Desktop Entry]
Type=Application
Name=OMIC UV
Exec=python3 $DESKTOP/run/main.py
Path=$DESKTOP/run
Icon=$DESKTOP/run/icon/durian.png
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

echo "✅ Installation complete. Reboot to start the app."