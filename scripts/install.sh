#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$HOME/.config/opencode/skills/okf-generator"

if ! command -v pip3 &>/dev/null; then
    echo "pip3 not found — install Python first: https://python.org"
    exit 1
fi

pip3 install --quiet --upgrade okf-generator[llm]

mkdir -p "$SKILL_DIR"
SKILL_URL="https://raw.githubusercontent.com/UmairBaig8/okf-generator/main/SKILL.md"
if ! [ -f "$SKILL_DIR/SKILL.md" ] && command -v curl &>/dev/null; then
    curl -fsSL "$SKILL_URL" -o "$SKILL_DIR/SKILL.md"
fi

echo "okf-generator installed. Restart Claude Code for the skill to load."
okf --help 2>/dev/null | head -5
