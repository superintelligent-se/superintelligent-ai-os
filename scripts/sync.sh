#!/bin/bash
# sync.sh — Automatisk git-sync för superintelligent-ai-os
# Kör via macOS LaunchAgent. Loggar till /tmp/superintelligent-sync.log
#
# Flöde: säkerhetskontroll → commit → pull --rebase → push → uppdatera WHATS-NEW.md
#
# Tips: skriv dina commit-meddelanden på klartext för att de ska dyka upp i WHATS-NEW.md.
# Exempel: "feat: Ny skill för inbox-triage — sorterar e-post automatiskt"
# Meddelanden som börjar med "chore:" filtreras bort automatiskt.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_FILE="/tmp/superintelligent-sync.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
HOSTNAME_SHORT=$(hostname -s)

log() {
  echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

# Håll loggen under 500 rader
if [ -f "$LOG_FILE" ] && [ "$(wc -l < "$LOG_FILE")" -gt 500 ]; then
  tail -300 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
fi

log "--- Sync startar på $HOSTNAME_SHORT ---"

# Verifiera att vi är i rätt repo
if [ ! -f "$REPO_DIR/CLAUDE.md" ]; then
  log "FEL: Kunde inte hitta CLAUDE.md i $REPO_DIR. Avbryter."
  exit 1
fi

cd "$REPO_DIR"

# Kontrollera att git-remote är tillgänglig
if ! git ls-remote --exit-code origin &>/dev/null; then
  log "VARNING: Kan inte nå GitHub. Hoppar över sync (ingen nätverksåtkomst?)."
  exit 0
fi

# --- KOLLA OM DET FINNS ÄNDRINGAR (exklusive WHATS-NEW.md) ---
CHANGED=$(git status --porcelain | grep -v "^??" | grep -v "WHATS-NEW.md" || true)

if [ -n "$CHANGED" ]; then
  log "Ändringar hittades:"
  git status --short | grep -v "^??" | grep -v "WHATS-NEW.md" | while read -r line; do log "  $line"; done

  # --- SÄKERHETSKONTROLL ---
  log "Kör säkerhetskontroll..."
  if ! bash "$REPO_DIR/scripts/safety-check.sh" >> "$LOG_FILE" 2>&1; then
    log "FEL: Säkerhetskontrollen misslyckades. Commit avbruten — granska manuellt."
    exit 1
  fi
  log "Säkerhetskontroll OK."

  # --- COMMIT ---
  # Om Claude har lämnat ett commit-meddelande under sessionen, använd det.
  # Annars: generisk nightly sync.
  PENDING_MSG="$REPO_DIR/.pending-commit-msg"
  if [ -f "$PENDING_MSG" ] && [ -s "$PENDING_MSG" ]; then
    COMMIT_MSG=$(cat "$PENDING_MSG")
    rm -f "$PENDING_MSG"
    log "Använder commit-meddelande från Claude: $COMMIT_MSG"
  else
    COMMIT_MSG="chore: nightly sync $(date '+%Y-%m-%d') [$HOSTNAME_SHORT]"
  fi
  git add -A -- ':!WHATS-NEW.md'
  git commit -m "$COMMIT_MSG" >> "$LOG_FILE" 2>&1
  log "Committade: $COMMIT_MSG"
else
  log "Inga lokala ändringar."
fi

# --- PULL ---
log "Hämtar senaste från origin/main..."
if ! git pull --rebase origin main >> "$LOG_FILE" 2>&1; then
  log "FEL: git pull --rebase misslyckades. Möjlig konflikt — lös manuellt."
  exit 1
fi

# --- PUSH (om vi committade något) ---
if [ -n "$CHANGED" ]; then
  log "Pushar till origin/main..."
  if ! git push origin main >> "$LOG_FILE" 2>&1; then
    log "FEL: git push misslyckades. Kör sync igen eller pusha manuellt."
    exit 1
  fi
  log "Push lyckades."
fi

# --- UPPDATERA WHATS-NEW.md ---
# Genererar en läsbar ändringslogg från git-historiken.
# Filterar bort "chore:"-commits — bara meningsfulla uppdateringar visas.
WHATS_NEW="$REPO_DIR/WHATS-NEW.md"
TMP_WHATS_NEW="/tmp/whats-new-generated.md"

{
  echo "# Nyheter — Superintelligent AI OS"
  echo ""
  echo "*Uppdateras automatiskt. Du behöver inte göra något.*"
  echo ""
  echo "---"
  echo ""

  # Hämta commits från senaste 90 dagarna, filtrera bort chore/nightly sync
  ENTRIES=$(git log \
    --format="%ad | %s" \
    --date=format:'%Y-%m-%d' \
    --since="90 days ago" \
    | grep -v "| chore:" \
    | grep -v "nightly sync" \
    | grep -v "update whats-new" \
    | head -25 || true)

  if [ -z "$ENTRIES" ]; then
    echo "*Inga nyheter de senaste 90 dagarna.*"
  else
    CURRENT_DATE=""
    while IFS='|' read -r date msg; do
      date=$(echo "$date" | tr -d ' ')
      msg=$(echo "$msg" | sed 's/^[[:space:]]*//' | sed 's/^[a-z]*: //')
      if [ "$date" != "$CURRENT_DATE" ]; then
        echo "### $date"
        CURRENT_DATE="$date"
      fi
      echo "- $msg"
    done <<< "$ENTRIES"
  fi

  echo ""
  echo "---"
  echo ""
  echo "*Äldre uppdateringar: [visa alla på GitHub](https://github.com/superintelligent-se/superintelligent-ai-os/commits/main)*"
} > "$TMP_WHATS_NEW"

# Jämför med befintlig fil — commit bara om något faktiskt ändrats
if ! diff -q "$TMP_WHATS_NEW" "$WHATS_NEW" &>/dev/null 2>&1; then
  cp "$TMP_WHATS_NEW" "$WHATS_NEW"
  git add WHATS-NEW.md
  git commit -m "chore: update whats-new" >> "$LOG_FILE" 2>&1
  git push origin main >> "$LOG_FILE" 2>&1
  log "WHATS-NEW.md uppdaterad och pushad."
else
  log "WHATS-NEW.md oförändrad."
fi

rm -f "$TMP_WHATS_NEW"
log "--- Sync klar ---"
