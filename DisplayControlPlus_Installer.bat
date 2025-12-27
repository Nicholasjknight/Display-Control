@echo off
title Display Control+ Installer
color 0A

echo.
echo ===============================================
echo     Display Control+ OLED Screen Protector
echo ===============================================
echo.

REM Check for existing installations
echo Checking for existing installations...
set EXISTING_FOUND=0

if exist "%APPDATA%\DisplayControlPlus" set EXISTING_FOUND=1
if exist "%APPDATA%\Display Control+" set EXISTING_FOUND=1
schtasks /query /tn "DisplayControlPlus_Background" >nul 2>&1 && set EXISTING_FOUND=1

if %EXISTING_FOUND%==1 (
    echo.
    echo WARNING: Existing Display Control+ installation detected!
    echo.
    echo For best results, please run "Complete_Cleanup.bat" first
    echo to remove all previous installations, then run this installer again.
    echo.
    echo Continue anyway? ^(This may cause conflicts^)
    choice /c YN /m "Press Y to continue or N to exit"
    if errorlevel 2 exit /b 1
)

echo.
echo This installer will:
echo  - Install Display Control+ to your system
echo  - Create a desktop shortcut
echo  - Set up automatic Windows startup
echo  - Configure background monitoring
echo.
pause

echo.
echo Installing Display Control+...
echo.

REM Create installation directory
if not exist "%APPDATA%\DisplayControlPlus" mkdir "%APPDATA%\DisplayControlPlus"

REM Copy all files from installer\dist\DisplayControlPlus to %APPDATA%\DisplayControlPlus
echo Copying application files...
xcopy /E /I /Y "installer\dist\DisplayControlPlus\*" "%APPDATA%\DisplayControlPlus\"

REM Copy config file to installation directory
echo Copying configuration...
copy /Y "config.json" "%APPDATA%\DisplayControlPlus\config.json" >nul

REM Copy logo/icon
copy /Y "Display Control+ Logo.png" "%APPDATA%\DisplayControlPlus\Display Control+ Logo.png" >nul
if exist "installer\Display Control+ Logo.ico" copy /Y "installer\Display Control+ Logo.ico" "%APPDATA%\DisplayControlPlus\Display Control+ Logo.ico" >nul

REM Create desktop shortcut using PowerShell
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Display Control+.lnk'); $Shortcut.TargetPath = '%APPDATA%\DisplayControlPlus\DisplayControlPlus.exe'; $Shortcut.WorkingDirectory = '%APPDATA%\DisplayControlPlus'; $Shortcut.Description = 'OLED Screen Protector - Prevent burn-in with smart overlays'; if (Test-Path '%APPDATA%\DisplayControlPlus\Display Control+ Logo.ico') { $Shortcut.IconLocation = '%APPDATA%\DisplayControlPlus\Display Control+ Logo.ico' }; $Shortcut.Save()"

REM Register background service for Windows startup
echo Setting up Windows startup service...
powershell -Command "try { $action = New-ScheduledTaskAction -Execute '%APPDATA%\DisplayControlPlus\DisplayControlPlus.exe' -Argument '--background' -WorkingDirectory '%APPDATA%\DisplayControlPlus'; $trigger = New-ScheduledTaskTrigger -AtLogOn; $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable; $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive; Register-ScheduledTask -TaskName 'DisplayControlPlus_Background' -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null; Write-Host 'Background service registered successfully' } catch { Write-Host 'Note: Background service registration requires admin rights' }"

echo.
echo ===============================================
echo           Installation Complete!
echo ===============================================
echo.
echo Desktop shortcut: Display Control+.lnk
echo Installation location: %APPDATA%\DisplayControlPlus
echo Background monitoring: Enabled on Windows startup
echo.
echo To get started:
echo  1. Double-click the desktop shortcut
echo  2. Configure your timeout and overlay preferences
echo  3. Click 'Apply' to activate protection
echo.
echo Your OLED screen is now protected!
echo.
pause
