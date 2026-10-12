@echo off
title Antigravity CLI (Mode Sans Permissions)
echo Lancement du CLI Antigravity avec auto-approbation de toutes les permissions...
echo (--dangerously-skip-permissions)
echo.
agy --dangerously-skip-permissions %*
