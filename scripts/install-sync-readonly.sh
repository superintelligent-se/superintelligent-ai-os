#!/bin/bash
# install-sync-readonly.sh — Installerar automatisk uppdatering av Superintelligent AI OS
#
# Kör detta en gång på din Mac. Därefter uppdateras skills automatiskt var 30:e minut.
# Du skriver aldrig något till GitHub — du hämtar bara.

set -euo pipefail

REPO_URL="https://github.com/superintelligent-se/superintelligent-ai-os.git"
INSTALL_DIR="$HOME/Documents/Superintelligent/superintelligent-ai-os"
PLIST_NAME="com.superintelligent.aios.sync-readonly"
PLIST_DEST="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"

echo ""
echo "Superintelligent AI OS — Kom igång"
echo "===================================="
echo ""

# --- STEG 1: Kontrollera att git finns ---
echo "Kontrollerar att Git är installerat..."
if ! command -v git &>/dev/null; then
  echo ""
  echo "  Git är inte installerat på den här datorn."
  echo "  Öppna App Store och installera 'Xcode Command Line Tools',"
  echo "  eller kör: xcode-select --install"
  echo "  Kör sedan det här skriptet igen."
  exit 1
fi
echo "  [OK] Git finns."

# --- STEG 2: Klona repot om det inte finns ---
echo ""
if [ -d "$INSTALL_DIR/.git" ]; then
  echo "  [OK] Repot finns redan på: $INSTALL_DIR"
else
  echo "Laddar ner Superintelligent AI OS till din dator..."
  mkdir -p "$(dirname "$INSTALL_DIR")"
  git clone "$REPO_URL" "$INSTALL_DIR" 2>&1 | grep -v "^$" || true
  echo "  [OK] Nedladdning klar: $INSTALL_DIR"
fi

# --- STEG 3: Skapa LaunchAgent-plist ---
echo ""
echo "Ställer in automatisk uppdatering (var 30:e minut)..."

mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST_DEST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${PLIST_NAME}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${INSTALL_DIR}/scripts/sync-readonly.sh</string>
  </array>
  <key>StartInterval</key>
  <integer>1800</integer>
  <key>RunAtLoad</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/tmp/superintelligent-sync.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/superintelligent-sync-error.log</string>
</dict>
</plist>
EOF

# Avlasta gammal version om den finns
launchctl unload "$PLIST_DEST" 2>/dev/null || true
launchctl load "$PLIST_DEST"

echo "  [OK] Automatisk uppdatering är aktiv."

# --- KLAR ---
echo ""
echo "===================================="
echo "Klar! Skills uppdateras nu automatiskt på den här datorn."
echo ""
echo "Nästa steg — öppna Claude Cowork:"
echo ""
echo "  1. Starta Claude på din Mac"
echo "  2. Klicka på 'Cowork' eller 'Open folder'"
echo "  3. Navigera till och välj den här mappen:"
echo ""
echo "     $INSTALL_DIR"
echo ""
echo "  4. Klart — Claude känner nu till alla Superintelligent-skills."
echo ""
echo "Vill du testa att allt fungerar? Kör:"
echo "  bash $INSTALL_DIR/scripts/sync-readonly.sh"
echo "  cat /tmp/superintelligent-sync.log"
echo ""
