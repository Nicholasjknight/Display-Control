@echo off
title Display Control+ - Easy Installation
color 0B
echo.
echo ================================================
echo    Display Control+ Professional Installation
echo ================================================
echo.
echo This will install Display Control+ Professional Edition
echo as a proper Windows application with desktop shortcuts.
echo.
echo What this installer does:
echo  ✓ Installs to Program Files (like real software)
echo  ✓ Creates desktop shortcut for easy access
echo  ✓ Adds Start Menu entry
echo  ✓ Sets up automatic OLED protection
echo  ✓ Includes uninstaller
echo.
echo Press any key to start installation...
pause >nul
echo.
echo Extracting and running installer...
cd /d "%~dp0"
powershell -Command "Expand-Archive -Path 'DisplayControlPlus_Production.zip' -DestinationPath 'TEMP_INSTALL' -Force"
cd TEMP_INSTALL
start /wait Professional_Installer.bat
cd ..
rmdir /s /q TEMP_INSTALL
echo.
echo Installation completed! Check your desktop for the shortcut.
pause
