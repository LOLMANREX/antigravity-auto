#!/usr/bin/env bash
# Antigravity CLI - Mode Sans Permissions (Linux)
echo "Lancement du CLI Antigravity avec auto-approbation de toutes les permissions..."
echo "(--dangerously-skip-permissions)"
echo ""
agy --dangerously-skip-permissions "$@"
