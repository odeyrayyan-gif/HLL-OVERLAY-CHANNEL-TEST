@echo off
title HLL Overlay Server
cd /d "%~dp0"
echo.

:: Add Python to PATH in case it was freshly installed
set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
set "PATH=%APPDATA%\Python\Python311\Scripts;%PATH%"
for /f "tokens=*" %%i in ('where python 2^>nul') do set PYPATH=%%i

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo  ============================================================
    echo   ERROR: Python not found!
    echo  ============================================================
    echo.
    echo   HOW TO INSTALL PYTHON:
    echo.
    echo   1. Open your browser and go to:
    echo      https://www.python.org/downloads/
    echo.
    echo   2. Click the big yellow "Download Python" button
    echo.
    echo   3. Run the installer that downloads
    echo.
    echo   4. IMPORTANT: On the first screen of the installer,
    echo      tick the box that says "Add Python to PATH"
    echo      before clicking Install Now
    echo.
    echo   5. Once installed, close this window and
    echo      double-click start.bat again
    echo.
    echo  ============================================================
    pause
    exit
)

echo  ============================================================
echo   HLL OVERLAY SERVER
echo  ============================================================
echo   Hub:  http://localhost:3000
echo   Keep this window open while streaming.
echo  ============================================================
echo.

:: Start server then open browser after short delay
start /b cmd /c "timeout /t 2 /nobreak >nul && start "" http://localhost:3000"
python DO_NOT_EDIT_server.py
pause
