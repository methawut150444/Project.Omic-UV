#!/bin/bash
set -euo pipefail
trap 'echo "[ERROR] line $LINENO: command failed" >&2' ERR

# ---------- Resolve paths ----------
if command -v xdg-user-dir >/dev/null 2>&1; then
  DESKTOP="$(xdg-user-dir DESKTOP)"
else
  DESKTOP="$HOME/Desktop"
fi
REPO_DIR="$DESKTOP/Project.Omic-UV"
AUTOSTART_DIR="$HOME/.config/autostart"
AUTOSTART_FILE="$AUTOSTART_DIR/omicuv.desktop"
DESKTOP_SHORTCUT="$DESKTOP/OmicUV.desktop"

EXEC_CMD="python3 \"$REPO_DIR/run/main.py\""
WORK_DIR="\"$REPO_DIR/run\""
ICON_PATH="\"$REPO_DIR/run/icon/durian.png\""

echo "[1/3] Ensure repo exists then update"
if [ -d "$REPO_DIR/.git" ]; then
  git -C "$REPO_DIR" fetch --all
  git -C "$REPO_DIR" reset --hard origin/main
else
  echo "Repo not found at '$REPO_DIR'. Cloning…"
  git clone https://github.com/methawut150444/Project.Omic-UV.git "$REPO_DIR"
fi

echo "[2/3] Refresh autostart entry"
mkdir -p "$AUTOSTART_DIR"
if [ -f "$AUTOSTART_FILE" ]; then
  sed -i "s|^Exec=.*|Exec=$EXEC_CMD|" "$AUTOSTART_FILE" || true
  sed -i "s|^Path=.*|Path=$WORK_DIR|" "$AUTOSTART_FILE" || true
  sed -i "s|^Icon=.*|Icon=$ICON_PATH|" "$AUTOSTART_FILE" || true
else
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
fi
chmod +x "$AUTOSTART_FILE"

echo "[3/3] Update Desktop shortcut (OmicUV.desktop) if present, otherwise create"
if [ -f "$DESKTOP_SHORTCUT" ]; then
  sed -i "s|^Exec=.*|Exec=$EXEC_CMD|" "$DESKTOP_SHORTCUT" || true
  sed -i "s|^Path=.*|Path=$WORK_DIR|" "$DESKTOP_SHORTCUT" || true
  sed -i "s|^Icon=.*|Icon=$ICON_PATH|" "$DESKTOP_SHORTCUT" || true
else
  cp "$AUTOSTART_FILE" "$DESKTOP_SHORTCUT" || true
fi
chmod +x "$DESKTOP_SHORTCUT" 2>/dev/null || true

echo "✅ Update done. Reboot to run the latest version."