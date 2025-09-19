#!/bin/bash
set -e

DESKTOP="$HOME/Desktop"

echo "[1/3] Remove old version if exists"
rm -rf "$DESKTOP/OMIC_UV"  # โฟลเดอร์เก่า
rm -rf "$DESKTOP/run"      # ถ้ามีเวอร์ชันเก่าของ run

echo "[2/3] Copy new version"
cp -r run "$DESKTOP/"

echo "[3/3] Update autostart file"
NEW_ICON="$DESKTOP/run/icon/durian.png"
DESKTOP_FILE="$HOME/.config/autostart/omicuv.desktop"

if [ -f "$DESKTOP_FILE" ]; then
  sed -i "s|^Exec=.*|Exec=python3 $DESKTOP/run/main.py|" "$DESKTOP_FILE"
  sed -i "s|^Icon=.*|Icon=$NEW_ICON|" "$DESKTOP_FILE"
fi

echo "✅ Update complete. Reboot to run the new version."