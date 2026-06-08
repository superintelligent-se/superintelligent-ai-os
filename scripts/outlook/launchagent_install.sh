#!/bin/bash
# launchagent_install.sh — Installerar Telegram-boten som macOS LaunchAgent.
#
# Boten startar automatiskt vid inloggning och startar om sig själv
# om den kraschar. Du behöver aldrig starta den manuellt igen.
#
# Kör: bash scripts/outlook/launchagent_install.sh

set -e

PLIST_NAME="se.superintelligent.telegram-bot"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$PLIST_DIR/$PLIST_NAME.plist"
VENV_PY="$HOME/.config/superintelligent/outlook-bridge/venv/bin/python3"
SCRIPT="$HOME/Github/Superintelligent/superintelligent-ai-os/scripts/outlook/telegram_bot.py"
LOG_DIR="$HOME/.config/superintelligent/outlook-bridge"

# Kontrollera att venv finns
if [ ! -f "$VENV_PY" ]; then
  echo "FEL: Venv saknas på $VENV_PY"
  echo "Kör setup-stegen i auth_setup.md först."
  exit 1
fi

# Kontrollera att scriptet finns
if [ ! -f "$SCRIPT" ]; then
  echo "FEL: telegram_bot.py saknas på $SCRIPT"
  exit 1
fi

mkdir -p "$PLIST_DIR"
mkdir -p "$LOG_DIR"

# Avinstallera befintlig agent om den finns
if launchctl list | grep -q "$PLIST_NAME" 2>/dev/null; then
  echo "Avinstallerar befintlig agent..."
  launchctl unload "$PLIST_FILE" 2>/dev/null || true
fi

# Skapa plist-filen
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_NAME}</string>

    <key>ProgramArguments</key>
    <array>
        <string>${VENV_PY}</string>
        <string>${SCRIPT}</string>
    </array>

    <!-- Starta vid inloggning -->
    <key>RunAtLoad</key>
    <true/>

    <!-- Starta om automatiskt om boten kraschar -->
    <key>KeepAlive</key>
    <true/>

    <!-- Vänta 10 sekunder innan omstart (undviker crash-loop) -->
    <key>ThrottleInterval</key>
    <integer>10</integer>

    <!-- Loggar -->
    <key>StandardOutPath</key>
    <string>${LOG_DIR}/bot.log</string>
    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/bot-error.log</string>

    <!-- Kör i rätt katalog -->
    <key>WorkingDirectory</key>
    <string>$(dirname $(dirname "$SCRIPT"))</string>
</dict>
</plist>
EOF

# Ladda agenten
launchctl load "$PLIST_FILE"

echo ""
echo "✓ LaunchAgent installerad: $PLIST_NAME"
echo "✓ Boten startar automatiskt vid nästa inloggning"
echo "✓ Boten startar om sig själv om den kraschar"
echo ""
echo "Loggar:"
echo "  Stdout: $LOG_DIR/bot.log"
echo "  Stderr: $LOG_DIR/bot-error.log"
echo ""
echo "Hantera boten:"
echo "  Stoppa:    launchctl stop $PLIST_NAME"
echo "  Starta:    launchctl start $PLIST_NAME"
echo "  Avinstall: launchctl unload $PLIST_FILE && rm $PLIST_FILE"
