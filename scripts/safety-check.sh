#!/bin/bash
# safety-check.sh — Kontrollerar vanliga risker innan commit

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ISSUES=0

echo "Superintelligent AI OS — Säkerhetskontroll"
echo "==========================================="
echo ""

# 1. Kontrollera .env-filer
echo "1. Letar efter .env-filer..."
ENV_FILES=$(find "$REPO_DIR" -name ".env" -o -name ".env.*" 2>/dev/null | grep -v ".gitignore" | grep -v "node_modules" || true)
if [ -n "$ENV_FILES" ]; then
  echo "   VARNING: Hittade .env-filer:"
  echo "$ENV_FILES" | sed 's/^/   - /'
  ISSUES=$((ISSUES + 1))
else
  echo "   [OK] Inga .env-filer hittades"
fi

# 2. Kontrollera nyckelfiler
echo ""
echo "2. Letar efter nyckelfiler (.key, .pem, .p12, .pfx)..."
KEY_FILES=$(find "$REPO_DIR" \( -name "*.key" -o -name "*.pem" -o -name "*.p12" -o -name "*.pfx" \) 2>/dev/null | grep -v "node_modules" || true)
if [ -n "$KEY_FILES" ]; then
  echo "   VARNING: Hittade nyckelfiler:"
  echo "$KEY_FILES" | sed 's/^/   - /'
  ISSUES=$((ISSUES + 1))
else
  echo "   [OK] Inga nyckelfiler hittades"
fi

# 3. Kontrollera privata mappar
echo ""
echo "3. Letar efter privata mappar..."
PRIVATE_DIRS=("data" "private" "client-data" "transcripts" "emails" "calendar" "secrets" "meeting-notes")
for dir in "${PRIVATE_DIRS[@]}"; do
  if [ -d "$REPO_DIR/$dir" ]; then
    echo "   VARNING: Mappen '$dir' finns i repot — ska den vara här?"
    ISSUES=$((ISSUES + 1))
  fi
done
if [ $ISSUES -eq 0 ]; then
  echo "   [OK] Inga privata mappar hittades"
fi

# 4. Kontrollera misstänkta secrets i filer
echo ""
echo "4. Letar efter misstänkta secrets i textfiler..."
SECRET_PATTERNS="(api_key|apikey|secret|password|token|bearer|authorization)\s*[:=]\s*['\"]?[A-Za-z0-9+/]{20,}"
SECRET_HITS=$(grep -rIiE "$SECRET_PATTERNS" "$REPO_DIR" \
  --exclude-dir=".git" \
  --exclude-dir="node_modules" \
  --exclude="*.example.*" \
  --exclude="safety-check.sh" \
  2>/dev/null || true)
if [ -n "$SECRET_HITS" ]; then
  echo "   VARNING: Misstänkta secrets hittades:"
  echo "$SECRET_HITS" | head -5 | sed 's/^/   /'
  ISSUES=$((ISSUES + 1))
else
  echo "   [OK] Inga misstänkta secrets hittades"
fi

# 5. Kontrollera settings.local.json
echo ""
echo "5. Kontrollerar att settings.local.json inte är staged..."
if git -C "$REPO_DIR" diff --cached --name-only 2>/dev/null | grep -q "settings.local.json"; then
  echo "   VARNING: settings.local.json är staged för commit — ta bort den!"
  ISSUES=$((ISSUES + 1))
else
  echo "   [OK] settings.local.json är inte staged"
fi

# Sammanfattning
echo ""
echo "==========================================="
if [ $ISSUES -eq 0 ]; then
  echo "Resultat: Inga problem hittades. Du kan committa."
  exit 0
else
  echo "Resultat: $ISSUES problem hittades. Lös dem innan du commitar."
  exit 1
fi
