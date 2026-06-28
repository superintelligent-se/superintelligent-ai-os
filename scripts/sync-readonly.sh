#!/bin/bash
# sync-readonly.sh — Hämtar senaste skills automatiskt från Superintelligent
# Kör via macOS LaunchAgent var 30:e minut. Skriver aldrig något till GitHub.

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_FILE="/tmp/superintelligent-sync.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

log() {
  echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
}

# Håll loggen under 300 rader
if [ -f "$LOG_FILE" ] && [ "$(wc -l < "$LOG_FILE")" -gt 300 ]; then
  tail -200 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
fi

log "--- Hämtar uppdateringar ---"

# Kontrollera nätverksåtkomst
if ! git -C "$REPO_DIR" ls-remote --exit-code origin &>/dev/null; then
  log "Ingen nätverksåtkomst. Försöker igen nästa gång."
  exit 0
fi

# Hämta senaste från GitHub
if git -C "$REPO_DIR" pull --ff-only origin main >> "$LOG_FILE" 2>&1; then
  log "Klart."
else
  log "Kunde inte hämta uppdateringar. Kontakta Superintelligent om problemet kvarstår."
fi
