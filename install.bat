@echo off
setlocal enabledelayedexpansion
title HLL Overlay TEST - Installer
color 0A

echo.
echo  ============================================================
echo   HLL COMMAND HUB TEST BUILD - INSTALLER
echo  ============================================================
echo.

set INSTALL_DIR=C:\HLL-Overlay-TEST
set GITHUB=https://raw.githubusercontent.com/odeyrayyan-gif/HLL-OVERLAY-TEST/main
set BACKUP_DIR=%TEMP%\HLL-Overlay-Backup

:: ── Check if this is a fresh install or reinstall ────────────
if exist "%INSTALL_DIR%" (
    echo   Existing installation found at %INSTALL_DIR%
    echo   This will do a clean reinstall - your API settings
    echo   and saved servers will be preserved.
    echo.
    pause

    :: Backup settings before wiping
    echo  [1/5] Backing up your settings...
    if exist "%BACKUP_DIR%" rmdir /s /q "%BACKUP_DIR%"
    mkdir "%BACKUP_DIR%"
    if exist "%INSTALL_DIR%\DO_NOT_EDIT_settings.json" (
        copy "%INSTALL_DIR%\DO_NOT_EDIT_settings.json" "%BACKUP_DIR%\" >nul
        echo        Saved: settings ^(API URL + saved servers^)
    )
    if exist "%INSTALL_DIR%\DO_NOT_EDIT_player.txt" (
        copy "%INSTALL_DIR%\DO_NOT_EDIT_player.txt" "%BACKUP_DIR%\" >nul
        echo        Saved: spotlight player name
    )

    :: Wipe the folder completely
    echo  [2/5] Removing old installation...
    rmdir /s /q "%INSTALL_DIR%"
    echo        Removed %INSTALL_DIR%
) else (
    echo   Fresh installation - no existing files found.
    echo.
    pause
    echo  [1/5] Skipping backup ^(fresh install^)...
    echo  [2/5] Skipping removal ^(fresh install^)...
)

:: ── Create fresh folder ───────────────────────────────────────
echo  [3/5] Creating %INSTALL_DIR%...
mkdir "%INSTALL_DIR%"
cd /d "%INSTALL_DIR%"
echo        Folder created.

:: ── Check for Python ─────────────────────────────────────────
echo.
echo        Checking for Python...
python --version >nul 2>&1
if %errorlevel% == 0 goto :python_ok
py --version >nul 2>&1
if %errorlevel% == 0 ( set PYTHON=py & goto :python_ok )

echo        Python not found. Downloading Python 3.11...
curl -L -o "%TEMP%\python_installer.exe" "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
if %errorlevel% neq 0 (
    echo  [!] Failed to download Python. Check your internet connection.
    pause & exit /b 1
)
echo        Installing Python silently...
"%TEMP%\python_installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
del "%TEMP%\python_installer.exe"
echo        Python installed.

:: Refresh PATH in current session so python is immediately available
:: Without this the current terminal won't find python until reopened
set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"

:: Verify python is now accessible
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [!] Python installed but PATH not updated yet.
    echo      Please close this window and run install.bat again.
    echo.
    pause
    exit /b 1
)
echo        Python verified and ready.

:python_ok
if not defined PYTHON set PYTHON=python

:: ── Download all files ────────────────────────────────────────
echo.
echo  [4/5] Downloading all HLL Overlay files from GitHub...
echo.

set FILES=DO_NOT_EDIT_server.py DO_NOT_EDIT_hub.html DO_NOT_EDIT_team_compare.html DO_NOT_EDIT_map_overlay.html DO_NOT_EDIT_at_leaderboard.html DO_NOT_EDIT_melee_leaderboard.html DO_NOT_EDIT_player_spotlight.html DO_NOT_EDIT_top5_scroll_banner.html DO_NOT_EDIT_top10_scroll_banner.html DO_NOT_EDIT_killstreaks.html DO_NOT_EDIT_killfeed.html DO_NOT_EDIT_tank_scoreboard.html DO_NOT_EDIT_message_banner.html DO_NOT_EDIT_settings.json DO_NOT_EDIT_player.txt version.txt changelog.md README.txt start.bat

for %%f in (%FILES%) do (
    echo        Downloading %%f...
    curl -L -s -o "%%f" "%GITHUB%/%%f"
    if !errorlevel! neq 0 echo  [!] Failed: %%f
)

:: ── Restore backed up settings ───────────────────────────────
echo.
if exist "%BACKUP_DIR%\DO_NOT_EDIT_settings.json" (
    copy "%BACKUP_DIR%\DO_NOT_EDIT_settings.json" "%INSTALL_DIR%\" >nul
    echo        Restored: API URL + saved servers
)
if exist "%BACKUP_DIR%\DO_NOT_EDIT_player.txt" (
    copy "%BACKUP_DIR%\DO_NOT_EDIT_player.txt" "%INSTALL_DIR%\" >nul
    echo        Restored: spotlight player name
)
if exist "%BACKUP_DIR%" rmdir /s /q "%BACKUP_DIR%"

:: ── Create desktop shortcut ───────────────────────────────────
echo.
echo  [5/5] Creating desktop shortcut...
:: Get actual desktop path via PowerShell (handles OneDrive-moved desktops)
for /f "usebackq delims=" %%D in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"`) do set DESKTOP=%%D
set SHORTCUT=!DESKTOP!\HLL Overlay TEST.lnk
powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut('!SHORTCUT!'); $sc.TargetPath = 'C:\HLL-Overlay-TEST\start.bat'; $sc.WorkingDirectory = 'C:\HLL-Overlay-TEST'; $sc.IconLocation = 'cmd.exe,0'; $sc.Description = 'HLL Command Hub'; $sc.Save()"
echo        Desktop shortcut created.

:: ── Done ─────────────────────────────────────────────────────
echo.
echo  ============================================================
echo   INSTALLATION COMPLETE!
echo  ============================================================
echo.
echo   Installed to: C:\HLL-Overlay
echo   Desktop shortcut: HLL Overlay TEST
echo.
echo   Starting HLL Overlay and opening hub...
echo.
timeout /t 2 /nobreak >nul

start "HLL Overlay TEST Server" /D "C:\HLL-Overlay-TEST" cmd /k "%PYTHON% DO_NOT_EDIT_server.py"
timeout /t 3 /nobreak >nul
:: Open browser - try multiple methods to handle admin/non-admin scenarios
start "" "http://localhost:3000"
if %errorlevel% neq 0 (
    rundll32 url.dll,FileProtocolHandler http://localhost:3000
)

echo   Done! The hub should open in your browser shortly.
echo   Use the desktop shortcut next time.
echo.
pause
