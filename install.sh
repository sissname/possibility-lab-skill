#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${CODEX_HOME:-$HOME/.codex}/skills"

mkdir -p "$TARGET_DIR"
rm -rf "$TARGET_DIR/possibility-lab"
cp -R "$ROOT_DIR/possibility-lab" "$TARGET_DIR/possibility-lab"

echo "Installed possibility-lab to $TARGET_DIR/possibility-lab"
echo "Next: copy config.example.json to config.local.json and add your Lark/Feishu Base token and table id."
