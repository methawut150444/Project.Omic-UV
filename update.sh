#!/bin/bash
set -e

DESKTOP="$HOME/Desktop"
APP_DIR="$DESKTOP/Project.Omic-UV"
AUTOSTART="$HOME/.config/autostart"
DESK_FILE="$DESKTOP/OmicUV.desktop"
AUTO_FILE="$AUTOSTART/omicuv.desktop"

echo "[1/3] Update repository"
if [ -d "$APP_DIR" ]; then
    cd "$APP_DIR"
    git pull
else
    git clone https://github.com/methawut150444/Project.Omic-UV.git "$APP_DIR"
    cd "$APP_DIR"
fi

echo "[2/3] Ensure dependencies (via apt)"
sudo apt install -y python3 python3-pyqt6 python3-opencv python3-gpiozero python3-picamera2 git

echo "[3/3] Fix Desktop & Autostart shortcuts"
mkdir -p "$AUTOSTART"

sed -i "s|^Exec=.*|Exec=python3 $APP_DIR/run/main.py|" "$DESK_FILE" "$AUTO_FILE" || true
sed -i "s|^Path=.*|Path=$APP_DIR/run|" "$DESK_FILE" "$AUTO_FILE" || true
sed -i "s|^Icon=.*|Icon=$APP_DIR/run/icon/durian.png|" "$DESK_FILE" "$AUTO_FILE" || true

chmod +x "$DESK_FILE" "$AUTO_FILE"

echo "✅ Update complete. Rebooting..."
sudo reboot