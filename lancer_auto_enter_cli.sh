#!/usr/bin/env bash
# Antigravity Auto-Enter Console (Linux)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/auto_enter_cli.py" --interval 1.0 --delay 3 "$@"
