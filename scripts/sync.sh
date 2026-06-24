#!/bin/bash
# sync.sh — Automatisk git-sync för superintelligent-ai-os
# Kör via macOS LaunchAgent. Loggar till /tmp/superintelligent-sync.log
#
# Flöde: säkerhetskontroll → commit → pull --rebase → push
# Commit sker före pull för att undvika konflikter med lokala ändringar.

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

# --- KOLLA OM DET FINNS ÄNDRINGAR ---
CHANGED=$(git status --porcelain | grep -v "^??" || true)  # Ignorera untracked files

if [ -n "$CHANGED" ]; then
  log "Ändringar hittades:"
  git status --short | grep -v "^??" | while read -r line; do log "  $line"; done

  # --- SÄKERHETSKONTROLL ---
  log "Kör säkerhetskontroll..."
  if ! bash "$REPO_DIR/scripts/safety-check.sh" >> "$LOG_FILE" 2>&1; then
    log "FEL: Säkerhetskontrollen misslyckades. Commit avbruten — granska manuellt."
    exit 1
  fi
  log "Säkerhetskontroll OK."

  # --- COMMIT ---
  COMMIT_MSG="chore: nightly sync $(date '+%Y-%m-%d') [$HOSTNAME_SHORT]"
  git add -A
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

log "--- Sync klar ---"
