#!/bin/bash
# package-skills.sh — Paketerar skills-mappen som ett arkiv för delning

set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUTPUT="$REPO_DIR/../superintelligent-skills-$TIMESTAMP.tar.gz"

echo "Paketerar skills..."
tar -czf "$OUTPUT" -C "$REPO_DIR" skills/

echo "Klar: $OUTPUT"
echo ""
echo "OBS: Kontrollera att arkivet inte innehåller privat data innan du delar det."
