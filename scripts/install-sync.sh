#!/bin/bash
# install-sync.sh — Installerar automatisk git-sync på denna maskin
# Kör en gång per maskin (MacBook Pro, Mac Mini, kollega osv.)
#
# Vad detta gör:
#   1. Sätter rätt repo-sökväg i LaunchAgent-plist
#   2. Kopierar plist till ~/Library/LaunchAgents/
#   3. Laddar LaunchAgent (startar automatisk sync)
#   4. Kontrollerar SSH-autentisering mot GitHub
#
# Förutsättning: SSH-nyckel måste vara tillagd i GitHub innan du kör detta.
# Se instruktionerna i README eller kör: ssh-keygen -t ed25519 -C "din@email.com"

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_NAME="com.superintelligent.aios.sync"
PLIST_SRC="$REPO_DIR/scripts/${PLIST_NAME}.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

echo "Superintelligent AI OS — Installerar git-sync"
echo "==============================================="
echo "Repo: $REPO_DIR"
echo "Maskin: $(hostname -s)"
echo ""

# --- STEG 1: SSH-kontroll ---
echo "Steg 1: Kontrollerar SSH-autentisering mot GitHub..."
SSH_RESULT=$(ssh -T git@github.com 2>&1 || true)
if echo "$SSH_RESULT" | grep -q "successfully authenticated"; then
  echo "  [OK] SSH fungerar mot GitHub."
else
  echo ""
  echo "  VARNING: SSH mot GitHub fungerar inte på den här maskinen."
  echo "  Gör så här för att sätta upp det:"
  echo ""
  echo "  1. Generera en SSH-nyckel (om du inte redan har en):"
  echo "     ssh-keygen -t ed25519 -C \"$(git config user.email 2>/dev/null || echo 'din@email.com')\""
  echo ""
  echo "  2. Kopiera nyckeln:"
  echo "     pbcopy < ~/.ssh/id_ed25519.pub"
  echo ""
  echo "  3. Lägg till den på GitHub:"
  echo "     https://github.com/settings/keys  →  New SSH key"
  echo ""
  echo "  4. Uppdatera remote-URL till SSH:"
  echo "     git -C \"$REPO_DIR\" remote set-url origin git@github.com:superintelligent-se/superintelligent-ai-os.git"
  echo ""
  echo "  5. Kör det här skriptet igen."
  echo ""
  read -rp "  Vill du fortsätta installationen ändå? (ja/nej): " CONTINUE
  if [[ "$CONTINUE" != "ja" ]]; then
    echo "  Installation avbruten. Sätt upp SSH och kör igen."
    exit 1
  fi
fi

# --- STEG 2: Uppdatera sökväg i plist ---
echo ""
echo "Steg 2: Konfigurerar LaunchAgent med rätt sökväg..."
mkdir -p "$LAUNCH_AGENTS_DIR"

# Ersätt platshållaren REPO_PATH med faktisk sökväg
sed "s|REPO_PATH|$REPO_DIR|g" "$PLIST_SRC" > "$PLIST_DEST"
echo "  [OK] Plist installerad: $PLIST_DEST"

# --- STEG 3: Ladda LaunchAgent ---
echo ""
echo "Steg 3: Startar LaunchAgent..."

# Avlasta gammal version om den finns
if launchctl list | grep -q "$PLIST_NAME" 2>/dev/null; then
  launchctl unload "$PLIST_DEST" 2>/dev/null || true
  echo "  [OK] Gammal version avlastad."
fi

launchctl load "$PLIST_DEST"
echo "  [OK] LaunchAgent laddad och aktiv."

# --- STEG 4: Verifiera ---
echo ""
echo "Steg 4: Verifierar..."
if launchctl list | grep -q "$PLIST_NAME"; then
  echo "  [OK] Sync-tjänsten körs."
else
  echo "  [FEL] LaunchAgent verkar inte ha startat. Kontrollera /tmp/superintelligent-sync-error.log"
  exit 1
fi

echo ""
echo "==============================================="
echo "Klar! Git-sync är nu aktiv på $(hostname -s)."
echo ""
echo "Sync körs automatiskt var 30:e minut."
echo "Loggar: /tmp/superintelligent-sync.log"
echo ""
echo "Kommandon:"
echo "  Visa logg:         tail -f /tmp/superintelligent-sync.log"
echo "  Kör sync nu:       bash $REPO_DIR/scripts/sync.sh"
echo "  Avaktivera sync:   launchctl unload $PLIST_DEST"
echo "  Aktivera igen:     launchctl load $PLIST_DEST"
