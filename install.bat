@echo off
echo Setting up Display Control+ for Windows startup...

REM Copy files to a permanent location
set INSTALL_DIR=%APPDATA%\DisplayControlPlus
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy the executable and dependencies
xcopy /Y /S "installer\dist\DisplayControlPlus\*" "%INSTALL_DIR%\"
copy /Y "dist\overlay_bg.exe" "%INSTALL_DIR%\"
copy /Y "config.json" "%INSTALL_DIR%\"
copy /Y "Display Control+ Logo.ico" "%INSTALL_DIR%\"

REM Create desktop shortcut
set DESKTOP=%USERPROFILE%\Desktop
echo [InternetShortcut] > "%DESKTOP%\Display Control+.url"
echo URL=file:///%INSTALL_DIR:\=/%/DisplayControlPlus.exe >> "%DESKTOP%\Display Control+.url"
echo IconFile=%INSTALL_DIR%\Display Control+ Logo.ico >> "%DESKTOP%\Display Control+.url"
echo IconIndex=0 >> "%DESKTOP%\Display Control+.url"

REM Create proper desktop shortcut using PowerShell
powershell -Command "$WScriptShell = New-Object -ComObject WScript.Shell; $Shortcut = $WScriptShell.CreateShortcut('%DESKTOP%\Display Control+.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\DisplayControlPlus.exe'; $Shortcut.IconLocation = '%INSTALL_DIR%\Display Control+ Logo.ico'; $Shortcut.Save()"

REM Create Task Scheduler entry for background service
schtasks /Create /TN "Display Control+ Background" /TR "\"%INSTALL_DIR%\overlay_bg.exe\"" /SC ONLOGON /RL HIGHEST /F

echo.
echo ===================================
echo Display Control+ Setup Complete!
echo ===================================
echo.
echo Desktop shortcut created: Display Control+.lnk
echo Background service scheduled for logon
echo.
echo To configure: Double-click desktop shortcut
echo To test: Settings are applied immediately
echo.
pause
