#!/bin/bash
set -euo pipefail
trap 'echo "[ERROR] line $LINENO: command failed" >&2' ERR

# ---------- Resolve paths ----------
if command -v xdg-user-dir >/dev/null 2>&1; then
  DESKTOP="$(xdg-user-dir DESKTOP)"
else
  DESKTOP="$HOME/Desktop"
fi
REPO_DIR="$DESKTOP/Project.Omic-UV"    # ที่อยู่ repo บน Desktop
AUTOSTART_DIR="$HOME/.config/autostart"
AUTOSTART_FILE="$AUTOSTART_DIR/omicuv.desktop"
DESKTOP_SHORTCUT="$DESKTOP/OmicUV.desktop"

EXEC_CMD="python3 \"$REPO_DIR/run/main.py\""
WORK_DIR="\"$REPO_DIR/run\""
ICON_PATH="\"$REPO_DIR/run/icon/durian.png\""

echo "[1/5] APT dependencies"
sudo apt update
sudo apt install -y git python3 python3-pip python3-pyqt6 python3-opencv python3-gpiozero python3-picamera2

echo "[2/5] Clone repo to Desktop (if missing)"
mkdir -p "$DESKTOP"
if [ ! -d "$REPO_DIR/.git" ]; then
  git clone https://github.com/methawut150444/Project.Omic-UV.git "$REPO_DIR"
else
  echo "Repo exists at '$REPO_DIR' -> skip clone."
fi

echo "[3/5] Python packages"
python3 -m pip install --upgrade pip
if [ -f "$REPO_DIR/requirements.txt" ]; then
  python3 -m pip install -r "$REPO_DIR/requirements.txt" || true
fi

echo "[4/5] Create/Update autostart"
mkdir -p "$AUTOSTART_DIR"
cat > "$AUTOSTART_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=OMIC UV
Exec=$EXEC_CMD
Path=$WORK_DIR
Icon=$ICON_PATH
Terminal=false
X-GNOME-Autostart-enabled=true
EOF
chmod +x "$AUTOSTART_FILE"

echo "[5/5] Fix existing Desktop shortcut (OmicUV.desktop) or create one"
if [ -f "$DESKTOP_SHORTCUT" ]; then
  sed -i "s|^Exec=.*|Exec=$EXEC_CMD|" "$DESKTOP_SHORTCUT" || true
  sed -i "s|^Path=.*|Path=$WORK_DIR|" "$DESKTOP_SHORTCUT" || true
  sed -i "s|^Icon=.*|Icon=$ICON_PATH|" "$DESKTOP_SHORTCUT" || true
else
  cp "$AUTOSTART_FILE" "$DESKTOP_SHORTCUT" || true
fi
chmod +x "$DESKTOP_SHORTCUT" 2>/dev/null || true

echo "✅ Install finished. Reboot to start the app automatically."