@echo off
echo Removing Display Control+ from Windows startup...

REM Remove Task Scheduler entry
schtasks /Delete /TN "Display Control+ Background" /F

REM Remove desktop shortcut
del "%USERPROFILE%\Desktop\Display Control+.lnk" /Q
del "%USERPROFILE%\Desktop\Display Control+.url" /Q

REM Remove installation directory
set INSTALL_DIR=%APPDATA%\DisplayControlPlus
if exist "%INSTALL_DIR%" rmdir /S /Q "%INSTALL_DIR%"

echo.
echo Display Control+ uninstalled successfully!
echo.
pause
