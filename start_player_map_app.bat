@echo off
title HLL Player Map App
cd /d "%~dp0"
echo.

set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
set "PATH=%APPDATA%\Python\Python311\Scripts;%PATH%"

python --version >nul 2>&1
if errorlevel 1 (
    echo  ============================================================
    echo   ERROR: Python not found!
    echo  ============================================================
    echo   Install Python from https://www.python.org/downloads/
    echo   Make sure "Add Python to PATH" is checked.
    echo  ============================================================
    pause
    exit
)

echo  ============================================================
echo   HLL PLAYER MAP APP
echo  ============================================================
echo   URL: http://localhost:3100
echo  ============================================================
echo.

start /b cmd /c "timeout /t 2 /nobreak >nul && start "" http://localhost:3100"
python "player_map_app/server.py"
pause
