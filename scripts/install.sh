#!/bin/bash
# install.sh — Installerar skills och verifierar repots struktur

set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo "Superintelligent AI OS — Installation"
echo "======================================"
echo "Repo: $REPO_DIR"
echo ""

# Kontrollera att vi är i rätt mapp
if [ ! -f "$REPO_DIR/CLAUDE.md" ]; then
  echo "FEL: Kunde inte hitta CLAUDE.md. Är du i rätt mapp?"
  exit 1
fi

# Verifiera mappstruktur
echo "Kontrollerar mappstruktur..."
REQUIRED_DIRS=("skills" "workflows" "templates" "connectors" "scripts")
for dir in "${REQUIRED_DIRS[@]}"; do
  if [ -d "$REPO_DIR/$dir" ]; then
    echo "  [OK] $dir/"
  else
    echo "  [SAKNAS] $dir/"
  fi
done

echo ""

# Kontrollera att .gitignore finns
if [ -f "$REPO_DIR/.gitignore" ]; then
  echo "[OK] .gitignore finns"
else
  echo "[VARNING] .gitignore saknas — skapa den innan du commitar"
fi

# Kör säkerhetskontrollen
echo ""
echo "Kör säkerhetskontroll..."
bash "$REPO_DIR/scripts/safety-check.sh"

echo ""
echo "Installation klar."
echo "Öppna repot i Claude Code med: claude ."
