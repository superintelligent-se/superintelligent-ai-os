#!/bin/bash
# setup_credentials.sh — Konfigurera API-nycklar för Telegram-assistenten.
#
# Körs EN gång (eller igen om du byter nycklar).
# Sparar allt i macOS Keychain — aldrig i repot.
#
# Kör: bash scripts/telegram/setup_credentials.sh

set -e

KEYCHAIN_SERVICE="superintelligent-telegram-bridge"
VENV_DIR="$HOME/.config/superintelligent/outlook-bridge/venv"
VENV_PIP="$VENV_DIR/bin/pip"
REQUIREMENTS="$(dirname "$0")/requirements.txt"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Telegram Assistant — Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── 1. Anthropic API-nyckel ───────────────────────────────────────────────────
echo "Steg 1/2: Anthropic API-nyckel"
echo "  Hitta den på: https://console.anthropic.com/settings/keys"
echo ""
read -rsp "  Klistra in Anthropic API-nyckel (visas ej): " ANTHROPIC_KEY
echo ""

if [ -z "$ANTHROPIC_KEY" ]; then
  echo "FEL: Anthropic API-nyckel får inte vara tom." >&2
  exit 1
fi

security add-generic-password \
  -s "$KEYCHAIN_SERVICE" \
  -a "anthropic-api-key" \
  -w "$ANTHROPIC_KEY" \
  -U 2>/dev/null || \
security add-generic-password \
  -s "$KEYCHAIN_SERVICE" \
  -a "anthropic-api-key" \
  -w "$ANTHROPIC_KEY"

echo "  ✓ Anthropic API-nyckel sparad i Keychain"
echo ""

# ── 2. Installera Python-paket i befintlig venv ───────────────────────────────
echo "Steg 2/2: Installera Python-paket"

if [ ! -f "$VENV_PIP" ]; then
  echo "FEL: Venv saknas på $VENV_DIR" >&2
  echo "Kör först: bash scripts/outlook/launchagent_install.sh (eller auth_setup.md)" >&2
  exit 1
fi

echo "  Installerar i: $VENV_DIR"
echo "  (openai-whisper kan ta ett par minuter första gången)"
"$VENV_PIP" install -q -r "$REQUIREMENTS"
echo "  ✓ Python-paket installerade"
echo ""

# ── Klar ──────────────────────────────────────────────────────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✓ Setup klar!"
echo ""
echo "  Nästa steg:"
echo "  1. Installera LaunchAgent:"
echo "     bash scripts/telegram/launchagent_install.sh"
echo ""
echo "  2. Testa boten manuellt:"
echo "     python scripts/telegram/assistant_bot.py"
echo ""
echo "  3. Skriv /help i Telegram för att verifiera."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
