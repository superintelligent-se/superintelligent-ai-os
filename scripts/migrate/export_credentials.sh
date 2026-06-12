#!/usr/bin/env bash
# =============================================================================
# export_credentials.sh — Exportera .secret/credentials.json säkert
#
# Krypterar credentials-filen med AES-256 och sparar den på skrivbordet.
# Kopiera sedan credentials_export.enc till Mac Mini och dekryptera där.
#
# Användning (kör från repo-roten på laptopen):
#   bash scripts/migrate/export_credentials.sh
#
# Dekryptering på Mac Mini:
#   openssl enc -d -aes-256-cbc -pbkdf2 \
#     -in ~/Desktop/credentials_export.enc \
#     -out .secret/credentials.json
#   chmod 600 .secret/credentials.json
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC}  $1"; }
err()  { echo -e "${RED}✗${NC} $1"; exit 1; }
info() { echo -e "${BLUE}→${NC} $1"; }

# Hitta repo-roten
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CREDENTIALS="$REPO_ROOT/.secret/credentials.json"
OUTPUT="$HOME/Desktop/credentials_export.enc"

echo ""
echo "════════════════════════════════════════════════"
echo "  Credentials Export — Superintelligent AI OS"
echo "════════════════════════════════════════════════"
echo ""

# Kontrollera att credentials finns
if [[ ! -f "$CREDENTIALS" ]]; then
  err "Hittade inte $CREDENTIALS"
fi
ok "Hittade credentials: $CREDENTIALS"

# Kontrollera att openssl finns
command -v openssl >/dev/null 2>&1 || err "openssl saknas"
ok "openssl tillgängligt"

# Validera att JSON är giltig
if ! python3 -c "import json; json.load(open('$CREDENTIALS'))" 2>/dev/null; then
  err "credentials.json är inte giltig JSON — kontrollera filen"
fi
ok "credentials.json är giltig JSON"

# Visa vilka nycklar som finns (utan att visa värdena)
info "Nycklar i credentials.json:"
python3 -c "
import json
data = json.load(open('$CREDENTIALS'))
for section, values in data.items():
    keys = list(values.keys()) if isinstance(values, dict) else ['(värde)']
    print(f'  {section}: {keys}')
"

echo ""
warn "Du behöver välja ett lösenord för krypteringen."
warn "Kom ihåg det — du behöver det på Mac Mini."
echo ""

# Kryptera
openssl enc -aes-256-cbc -pbkdf2 -in "$CREDENTIALS" -out "$OUTPUT"

echo ""
ok "Exporterad till: $OUTPUT"
echo ""
echo "════════════════════════════════════════════════"
echo ""
echo "Nästa steg:"
echo ""
echo "  1. Kopiera filen till Mac Mini:"
echo "     AirDrop, eller via terminalen:"
echo "     scp ~/Desktop/credentials_export.enc mac-mini:~/Desktop/"
echo ""
echo "  2. Dekryptera på Mac Mini (kör från repo-roten):"
echo "     mkdir -p .secret"
echo "     openssl enc -d -aes-256-cbc -pbkdf2 \\"
echo "       -in ~/Desktop/credentials_export.enc \\"
echo "       -out .secret/credentials.json"
echo "     chmod 600 .secret/credentials.json"
echo ""
echo "  3. Ta bort exportfilen från båda maskiner efter dekryptering:"
echo "     rm ~/Desktop/credentials_export.enc"
echo ""
echo "  4. Verifiera på Mac Mini:"
echo "     python3 scripts/outlook/reauth.py"
echo ""
