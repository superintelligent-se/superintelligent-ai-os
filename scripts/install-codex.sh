#!/bin/bash
# Installerar repots kanoniska skills för Codex genom lokala symlänkar.
# Källfilerna ligger kvar i repot och används även av andra AI-klienter.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
TARGET_DIR="$CODEX_DIR/skills"

mkdir -p "$TARGET_DIR"

installed=0
skipped=0

for source_dir in "$REPO_DIR"/skills/*; do
  [[ -d "$source_dir" && -f "$source_dir/SKILL.md" ]] || continue

  skill_name="$(basename "$source_dir")"
  target="$TARGET_DIR/$skill_name"

  if [[ -L "$target" && "$(readlink "$target")" == "$source_dir" ]]; then
    echo "Redan installerad: $skill_name"
    continue
  fi

  if [[ -e "$target" || -L "$target" ]]; then
    echo "Hoppar över $skill_name: $target finns redan och ersätts inte." >&2
    skipped=$((skipped + 1))
    continue
  fi

  ln -s "$source_dir" "$target"
  echo "Installerad: $skill_name"
  installed=$((installed + 1))
done

echo "Codex-installation klar: $installed installerade, $skipped överhoppade."
echo "Starta om Codex om en ny skill inte visas direkt."
