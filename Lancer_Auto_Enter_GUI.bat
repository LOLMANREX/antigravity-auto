@echo off
title Antigravity Auto-Enter GUI
cd /d "%~dp0"
start "" pythonw auto_enter_app.py
if %ERRORLEVEL% NEQ 0 (
    python auto_enter_app.py
)
