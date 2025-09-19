#!/bin/bash
set -euo pipefail
trap 'echo "[ERROR] line $LINENO: command failed" >&2' ERR

echo "=== OMIC UV Installer (final, no-pip) ==="

# ---------- Resolve paths (Desktop, repo on Desktop) ----------
if command -v xdg-user-dir >/dev/null 2>&1; then
  DESKTOP="$(xdg-user-dir DESKTOP)"
else
  DESKTOP="$HOME/Desktop"
fi
REPO_DIR="$DESKTOP/Project.Omic-UV"         # repo target (ตาม README)
AUTOSTART_DIR="$HOME/.config/autostart"
AUTOSTART_FILE="$AUTOSTART_DIR/omicuv.desktop"
DESKTOP_SHORTCUT="$DESKTOP/OmicUV.desktop"

EXEC_CMD="python3 \"$REPO_DIR/run/main.py\""
WORK_DIR="\"$REPO_DIR/run\""
ICON_PATH="\"$REPO_DIR/run/icon/durian.png\""

# ---------- 1) System deps via APT (no pip needed) ----------
echo "[1/4] Install APT dependencies"
sudo apt update
sudo apt install -y \
  git python3 python3-pip \
  python3-pyqt6 python3-opencv python3-gpiozero python3-picamera2

# ---------- 2) Ensure repo is at ~/Desktop/Project.Omic-UV ----------
echo "[2/4] Ensure repository exists on Desktop"
mkdir -p "$DESKTOP"
if [ ! -d "$REPO_DIR/.git" ]; then
  echo "Cloning repository to $REPO_DIR"
  git clone https://github.com/methawut150444/Project.Omic-UV.git "$REPO_DIR"
else
  echo "Repo exists at '$REPO_DIR' — skipping clone."
fi

# ---------- 3) Create/Update autostart .desktop ----------
echo "[3/4] Create/Update autostart entry"
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

# ---------- 4) Fix existing desktop shortcut or create one ----------
echo "[4/4] Fix Desktop shortcut (OmicUV.desktop) or create it"
if [ -f "$DESKTOP_SHORTCUT" ]; then
  sed -i "s|^Exec=.*|Exec=$EXEC_CMD|" "$DESKTOP_SHORTCUT" || true
  sed -i "s|^Path=.*|Path=$WORK_DIR|" "$DESKTOP_SHORTCUT" || true
  sed -i "s|^Icon=.*|Icon=$ICON_PATH|" "$DESKTOP_SHORTCUT" || true
else
  cp "$AUTOSTART_FILE" "$DESKTOP_SHORTCUT" || true
fi
chmod +x "$DESKTOP_SHORTCUT" 2>/dev/null || true

echo "✅ Install complete."
echo "👉 Reboot to auto-start the app. (sudo reboot)"