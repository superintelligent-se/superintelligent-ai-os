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

# Spara hash på WHATS-NEW.md innan pull — för att detektera nyheter
WHATS_NEW="$REPO_DIR/WHATS-NEW.md"
BEFORE_HASH=""
if [ -f "$WHATS_NEW" ]; then
  BEFORE_HASH=$(md5 -q "$WHATS_NEW" 2>/dev/null || md5sum "$WHATS_NEW" 2>/dev/null | cut -d' ' -f1 || true)
fi

# Hämta senaste från GitHub
if ! git -C "$REPO_DIR" pull --ff-only origin main >> "$LOG_FILE" 2>&1; then
  log "Kunde inte hämta uppdateringar. Kontakta Superintelligent om problemet kvarstår."
  exit 0
fi

# Kontrollera om WHATS-NEW.md ändrades
if [ -f "$WHATS_NEW" ]; then
  AFTER_HASH=$(md5 -q "$WHATS_NEW" 2>/dev/null || md5sum "$WHATS_NEW" 2>/dev/null | cut -d' ' -f1 || true)
  if [ "$BEFORE_HASH" != "$AFTER_HASH" ]; then
    log "*** NYHETER TILLGÄNGLIGA — fråga Claude: 'vad är nytt?' ***"
  fi
fi

log "Klart."
