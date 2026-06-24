#!/bin/bash
# launchagent_install.sh — Installerar Telegram-assistenten som macOS LaunchAgent.
#
# Assistenten startar automatiskt vid inloggning och startar om sig om den kraschar.
# Ersätter eventuell befintlig telegram-bot LaunchAgent.
#
# Kör: bash scripts/telegram/launchagent_install.sh

set -e

PLIST_NAME="se.superintelligent.telegram-bot"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$PLIST_DIR/$PLIST_NAME.plist"
VENV_PY="$HOME/.config/superintelligent/outlook-bridge/venv/bin/python3"
SCRIPT="$HOME/Github/Superintelligent/superintelligent-ai-os/scripts/telegram/assistant_bot.py"
LOG_DIR="$HOME/.config/superintelligent/outlook-bridge"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Telegram Assistant — LaunchAgent"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Kontrollera venv
if [ ! -f "$VENV_PY" ]; then
  echo "FEL: Venv saknas på $VENV_PY" >&2
  echo "Kör setup_credentials.sh eller auth_setup.md (outlook) först." >&2
  exit 1
fi

# Kontrollera script
if [ ! -f "$SCRIPT" ]; then
  echo "FEL: assistant_bot.py saknas på $SCRIPT" >&2
  exit 1
fi

mkdir -p "$PLIST_DIR" "$LOG_DIR"

# Avregistrera och ta bort eventuell gammal agent
if launchctl list 2>/dev/null | grep -q "$PLIST_NAME"; then
  echo "  Avinstallerar befintlig agent…"
  launchctl unload "$PLIST_FILE" 2>/dev/null || true
fi

# Skapa plist
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_NAME}</string>

    <key>ProgramArguments</key>
    <array>
        <string>${VENV_PY}</string>
        <string>${SCRIPT}</string>
    </array>

    <!-- Starta automatiskt vid inloggning -->
    <key>RunAtLoad</key>
    <true/>

    <!-- Starta om automatiskt vid krasch -->
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

    <!-- Arbetskatalog = repots rot -->
    <key>WorkingDirectory</key>
    <string>$(dirname $(dirname "$SCRIPT"))</string>
</dict>
</plist>
EOF

# Ladda och starta agenten
launchctl load "$PLIST_FILE"

echo "  ✓ LaunchAgent installerad och startad"
echo ""
echo "  Bot:     @se.superintelligent.telegram-bot"
echo "  Script:  $SCRIPT"
echo "  Log:     $LOG_DIR/bot.log"
echo "  Err:     $LOG_DIR/bot-error.log"
echo ""
echo "  Hantera:"
echo "    Stoppa:      launchctl stop $PLIST_NAME"
echo "    Starta:      launchctl start $PLIST_NAME"
echo "    Loggar:      tail -f $LOG_DIR/bot.log"
echo "    Avinstall:   launchctl unload $PLIST_FILE && rm $PLIST_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
