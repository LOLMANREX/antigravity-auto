@echo off
title Antigravity Auto-Enter Console
cd /d "%~dp0"
python auto_enter_cli.py --interval 1.0 --delay 3
pause
