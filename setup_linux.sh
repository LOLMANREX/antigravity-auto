#!/usr/bin/env bash
# ==============================================================================
# Antigravity Auto - Setup Linux (Redirige vers install.sh)
# ==============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$SCRIPT_DIR/install.sh" "$@"
