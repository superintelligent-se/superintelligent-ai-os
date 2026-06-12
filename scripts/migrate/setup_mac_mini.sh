#!/usr/bin/env bash
# =============================================================================
# setup_mac_mini.sh — Bootstrap-skript för Mac Mini-migrering
# Kör detta på Mac Mini efter att du installerat Git och Python 3.
#
# Användning:
#   bash ~/setup_mac_mini.sh
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

echo ""
echo "════════════════════════════════════════════════"
echo "  Superintelligent AI OS — Mac Mini Setup"
echo "════════════════════════════════════════════════"
echo ""

# -----------------------------------------------------------
# 1. Kontrollera beroenden
# -----------------------------------------------------------
info "Kontrollerar beroenden..."

command -v git    >/dev/null 2>&1 || err "Git saknas. Kör: brew install git"
command -v python3 >/dev/null 2>&1 || err "Python 3 saknas. Kör: brew install python"

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [[ "$PYTHON_MAJOR" -lt 3 ]] || [[ "$PYTHON_MAJOR" -eq 3 && "$PYTHON_MINOR" -lt 9 ]]; then
  err "Python 3.9+ krävs. Hittad: $PYTHON_VERSION"
fi
ok "Python $PYTHON_VERSION"
ok "Git $(git --version | awk '{print $3}')"

# -----------------------------------------------------------
# 2. Skapa katalogstruktur
# -----------------------------------------------------------
info "Skapar katalogstruktur..."

REPO_PARENT="$HOME/Github/Superintelligent"
REPO_PATH="$REPO_PARENT/superintelligent-ai-os"

mkdir -p "$REPO_PARENT"
ok "Katalog: $REPO_PARENT"

# -----------------------------------------------------------
# 3. Klona eller uppdatera repot
# -----------------------------------------------------------
if [[ -d "$REPO_PATH/.git" ]]; then
  info "Repot finns redan — uppdaterar..."
  git -C "$REPO_PATH" pull origin main
  ok "Repo uppdaterat"
else
  info "Klonar superintelligent-ai-os..."
  git clone git@github.com:Superintelligent-se/superintelligent-ai-os.git "$REPO_PATH" \
    || git clone https://github.com/Superintelligent-se/superintelligent-ai-os.git "$REPO_PATH"
  ok "Repo klonat till $REPO_PATH"
fi

cd "$REPO_PATH"

# -----------------------------------------------------------
# 4. Sätt upp Python virtual environment
# -----------------------------------------------------------
info "Sätter upp Python virtual environment..."

if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
  ok "Virtual environment skapat"
else
  ok "Virtual environment finns redan"
fi

# Aktivera
# shellcheck disable=SC1091
source .venv/bin/activate

# -----------------------------------------------------------
# 5. Installera Python-paket
# -----------------------------------------------------------
info "Installerar Python-paket..."

pip install --quiet --upgrade pip

# Core-paket som scripts/outlook/ behöver
pip install --quiet requests msal

# Telegram-bot (om den ska köras lokalt)
if [[ -f "scripts/telegram/requirements.txt" ]]; then
  pip install --quiet -r scripts/telegram/requirements.txt
  ok "Telegram-paket installerade"
fi

ok "Python-paket klara"

# -----------------------------------------------------------
# 6. Skapa .secret/ om den saknas
# -----------------------------------------------------------
info "Kontrollerar .secret/..."

mkdir -p .secret
chmod 700 .secret

if [[ -f ".secret/credentials.json" ]]; then
  ok "credentials.json finns redan"
else
  warn "credentials.json saknas — du behöver kopiera den manuellt (se guiden, steg 2d)"
  warn "Kommando att köra efter kopiering:"
  echo ""
  echo "  openssl enc -d -aes-256-cbc -pbkdf2 \\"
  echo "    -in ~/Desktop/credentials_export.enc \\"
  echo "    -out $REPO_PATH/.secret/credentials.json"
  echo "  chmod 600 $REPO_PATH/.secret/credentials.json"
  echo ""
fi

# -----------------------------------------------------------
# 7. Verifiera git-konfiguration
# -----------------------------------------------------------
info "Kontrollerar git-konfiguration..."

GIT_USER=$(git config user.name 2>/dev/null || echo "")
GIT_EMAIL=$(git config user.email 2>/dev/null || echo "")

if [[ -z "$GIT_USER" ]]; then
  git config --global user.name "Thomas Dalebring"
  ok "Git user.name satt"
fi

if [[ -z "$GIT_EMAIL" ]]; then
  git config --global user.email "thomas@superintelligent.se"
  ok "Git user.email satt"
fi

ok "Git: $(git config user.name) <$(git config user.email)>"

# Verifiera SSH-åtkomst till GitHub
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
  ok "GitHub SSH-åtkomst verifierad"
else
  warn "GitHub SSH-åtkomst kunde inte verifieras."
  warn "Lägg till din SSH-nyckel på github.com/settings/keys"
  warn "Publik nyckel:"
  if [[ -f "$HOME/.ssh/id_ed25519.pub" ]]; then
    cat "$HOME/.ssh/id_ed25519.pub"
  else
    warn "Ingen SSH-nyckel hittad. Skapa en med: ssh-keygen -t ed25519 -C thomas@superintelligent.se"
  fi
fi

# -----------------------------------------------------------
# 8. Snabbtest av scripts (om credentials finns)
# -----------------------------------------------------------
if [[ -f ".secret/credentials.json" ]]; then
  info "Testar credentials..."
  if python3 scripts/outlook/reauth.py >/dev/null 2>&1; then
    ok "MS Graph token OK (reauth lyckades)"
  else
    warn "reauth.py misslyckades — token kan vara för gammal. Kör: python3 scripts/outlook/reauth.py"
  fi
fi

# -----------------------------------------------------------
# 9. Färdig
# -----------------------------------------------------------
echo ""
echo "════════════════════════════════════════════════"
echo -e "${GREEN}  Setup klar!${NC}"
echo "════════════════════════════════════════════════"
echo ""
echo "Nästa steg:"
echo "  1. Kopiera credentials_export.enc till Mac Mini och dekryptera (steg 2d i guiden)"
echo "  2. Installera Claude-appen och logga in med thomas@superintelligent.se"
echo "  3. Installera Productivity-plugin + anslut MS365"
echo "  4. Välj $REPO_PATH som workspace i Cowork"
echo "  5. Skapa scheduled tasks (se guiden, steg 4)"
echo "  6. Inaktivera tasks på laptopen"
echo ""
echo "Repo: $REPO_PATH"
echo "Python env: $REPO_PATH/.venv"
echo ""
