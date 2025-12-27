@echo off
title Display Control+ Auto-Setup
color 0B

echo.
echo ===============================================
echo     Display Control+ Auto-Setup
echo ===============================================
echo.
echo Welcome! This will automatically set up Display Control+.
echo.

REM Check if we're in a ZIP extraction directory
if not exist "DisplayControlPlus_Installer.bat" (
    echo Error: Installation files not found in current directory.
    echo Please extract the ZIP file completely and run this again.
    echo.
    pause
    exit /b 1
)

echo Starting installation process...
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This installer requires administrator privileges.
    echo Please right-click and "Run as administrator"
    echo.
    pause
    exit /b 1
)

REM Run the main installer
call "DisplayControlPlus_Installer.bat"

echo.
echo ===============================================
echo     Auto-Setup Complete!
echo ===============================================
echo.
echo Display Control+ has been installed and configured.
echo Check your desktop for the shortcut to configure settings.
echo.
pause
