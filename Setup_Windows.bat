@echo off
setlocal enabledelayedexpansion
title Installation d'Antigravity Auto pour Windows
color 0B

echo ============================================================
echo   Installation d'Antigravity Auto pour Windows
echo ============================================================
echo.

if exist "%~dp0Setup.exe" (
    echo [i] Lancement de l'installateur graphique Setup.exe...
    start "" "%~dp0Setup.exe"
    exit /b 0
)

echo [1/4] Preparation des repertoires...
set "TARGET_BIN=%LOCALAPPDATA%\agy\bin"
set "TARGET_SHARE=%LOCALAPPDATA%\antigravity-auto"
if not exist "%TARGET_BIN%" mkdir "%TARGET_BIN%"
if not exist "%TARGET_SHARE%" mkdir "%TARGET_SHARE%"

echo [2/4] Copie des commandes agy-auto et agy-yolo...
copy /y "%~dp0auto_enter_cli.py" "%TARGET_SHARE%\" >nul 2>&1
copy /y "%~dp0auto_enter_app.py" "%TARGET_SHARE%\" >nul 2>&1

(
echo @echo off
echo agy --dangerously-skip-permissions %%*
) > "%TARGET_BIN%\agy-auto.bat"

(
echo @echo off
echo agy --dangerously-skip-permissions %%*
) > "%TARGET_BIN%\agy-yolo.bat"

(
echo @echo off
echo python "%TARGET_SHARE%\auto_enter_cli.py" %%*
) > "%TARGET_BIN%\agy-enter.bat"

echo [3/4] Configuration automatique de settings.json...
set "SETTINGS_DIR=%USERPROFILE%\.gemini\antigravity-cli"
if not exist "%SETTINGS_DIR%" mkdir "%SETTINGS_DIR%"
powershell -NoProfile -Command ^
  "$path = Join-Path $env:USERPROFILE '.gemini\antigravity-cli\settings.json';" ^
  "$json = @{ toolPermission='always-proceed'; artifactReviewPolicy='always-proceed'; trustedWorkspaces=@($env:USERPROFILE) };" ^
  "Set-Content -Path $path -Value (ConvertTo-Json $json -Depth 5 -Compress:$false);"

echo [4/4] Verification du PATH utilisateur...
powershell -NoProfile -Command ^
  "$bin = [System.Environment]::ExpandEnvironmentVariables('%%LOCALAPPDATA%%\agy\bin');" ^
  "$p = [System.Environment]::GetEnvironmentVariable('Path', 'User');" ^
  "if (-not $p.Contains($bin)) { [System.Environment]::SetEnvironmentVariable('Path', $p + ';' + $bin, 'User'); }"

echo.
echo ============================================================
echo   Installation Windows terminee avec succes !
echo ============================================================
echo   Vous pouvez maintenant taper dans n'importe quel terminal :
echo     agy-auto
echo     agy-yolo
echo ============================================================
echo.
pause
