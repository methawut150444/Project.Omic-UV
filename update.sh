#!/bin/bash
set -e

DESKTOP="$HOME/Desktop"
APP_DIR="$DESKTOP/Project.Omic-UV"
AUTOSTART_DIR="$HOME/.config/autostart"
DESK_FILE="$DESKTOP/OmicUV.desktop"
AUTO_FILE="$AUTOSTART_DIR/omicuv.desktop"

echo "[1/3] Update repository"
mkdir -p "$DESKTOP"
if [ -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" fetch --all
  git -C "$APP_DIR" reset --hard origin/main
else
  git clone https://github.com/methawut150444/Project.Omic-UV.git "$APP_DIR"
fi

echo "[2/3] Ensure dependencies (apt only)"
sudo apt update
sudo apt install -y python3 python3-pyqt6 python3-opencv python3-gpiozero python3-picamera2 git

echo "[3/3] Rewrite Desktop & Autostart shortcuts"
mkdir -p "$AUTOSTART_DIR"

# Desktop shortcut
cat > "$DESK_FILE" <<EOF
[Desktop Entry]
Name=Omic UV App
Comment=Raspberry Pi GUI for UV Analysis
Exec=python3 $APP_DIR/run/main.py
Path=$APP_DIR/run
Icon=$APP_DIR/run/icon/durian.png
Terminal=false
Type=Application
Categories=Utility;
StartupNotify=false
EOF

# Autostart shortcut
cat > "$AUTO_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Omic UV
Exec=python3 $APP_DIR/run/main.py
Path=$APP_DIR/run
Icon=$APP_DIR/run/icon/durian.png
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

chmod +x "$DESK_FILE" "$AUTO_FILE"

echo "✅ Update complete. Rebooting..."
sudo reboot