@echo off
title Display Control+ Distribution Builder v2.0
color 0A

echo ===============================================
echo     Display Control+ Distribution Builder v2.0
echo ===============================================
echo.

REM Clean previous builds
echo [1/8] Cleaning previous distribution files...
if exist "DisplayControlPlus_Production" rmdir /s /q "DisplayControlPlus_Production"
if exist "DisplayControlPlus_Production.zip" del "DisplayControlPlus_Production.zip"

REM Create production directory structure
echo [2/8] Creating production directory structure...
mkdir "DisplayControlPlus_Production"
mkdir "DisplayControlPlus_Production\Application"
mkdir "DisplayControlPlus_Production\Documentation"
mkdir "DisplayControlPlus_Production\Tools"

REM Copy main application files
echo [3/8] Copying main application...
xcopy "dist\DisplayControlPlus\*" "DisplayControlPlus_Production\Application\" /E /I /Y

REM Copy configuration and assets
echo [4/8] Copying configuration files...
copy "config.json" "DisplayControlPlus_Production\Application\"
if exist "assets" xcopy "assets\*" "DisplayControlPlus_Production\Application\assets\" /E /I /Y
copy "Display Control+ Logo.png" "DisplayControlPlus_Production\Application\"

REM Create enhanced installer
echo [5/8] Creating enhanced installer...
echo @echo off > "DisplayControlPlus_Production\Professional_Installer.bat"
echo title Display Control+ Professional Installer >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo color 0B >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo. >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo ================================================ >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo     Display Control+ Professional Edition >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo        OLED Screen Protection Software >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo ================================================ >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo. >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo Welcome to Display Control+ Professional! >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo. >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo This installer will: >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo  - Install Display Control+ to Program Files >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo  - Create desktop and Start Menu shortcuts >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo  - Configure automatic Windows startup >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo  - Set up background OLED protection service >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo. >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo pause >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo. >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo REM Check admin rights >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo net session ^>nul 2^>^&1 >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo if %%errorLevel%% neq 0 ( >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo     echo ERROR: Administrator privileges required! >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo     echo Please right-click and "Run as administrator" >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo     echo. >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo     pause >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo     exit /b 1 >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo ^) >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo [1/4] Installing to Program Files... >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo if not exist "C:\Program Files\DisplayControlPlus" mkdir "C:\Program Files\DisplayControlPlus" >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo xcopy "Application\*" "C:\Program Files\DisplayControlPlus\" /E /I /Y ^>nul >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo [2/4] Creating desktop shortcut... >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%%USERPROFILE%%\Desktop\Display Control+.lnk'); $Shortcut.TargetPath = 'C:\Program Files\DisplayControlPlus\DisplayControlPlus.exe'; $Shortcut.Save()" >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo [3/4] Creating Start Menu shortcut... >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo if not exist "%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\Display Control Plus" mkdir "%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\Display Control Plus" >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\Display Control Plus\Display Control+.lnk'); $Shortcut.TargetPath = 'C:\Program Files\DisplayControlPlus\DisplayControlPlus.exe'; $Shortcut.Save()" >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo [4/4] Setting up automatic startup... >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo schtasks /create /tn "DisplayControlPlus_Background" /tr "C:\Program Files\DisplayControlPlus\DisplayControlPlus.exe --background" /sc onlogon /rl highest /f ^>nul 2^>^&1 >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo. >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo ================================================ >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo     Installation Complete! >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo ================================================ >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo. >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo Display Control+ has been successfully installed. >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo. >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo Check your desktop for the shortcut to configure settings. >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo Background protection is now active! >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo echo. >> "DisplayControlPlus_Production\Professional_Installer.bat"
echo pause >> "DisplayControlPlus_Production\Professional_Installer.bat"

REM Create professional uninstaller
echo [6/8] Creating professional uninstaller...
echo @echo off > "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo title Display Control+ Professional Uninstaller >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo color 0C >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo echo. >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo echo ================================================ >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo echo     Display Control+ Professional Uninstaller >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo echo ================================================ >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo echo. >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo echo WARNING: This will completely remove Display Control+ >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo echo from your system including all settings. >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo echo. >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo set /p confirm="Continue? (Y/N): " >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo if /i not "%%confirm%%"=="Y" exit /b 0 >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo echo. >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo net session ^>nul 2^>^&1 >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo if %%errorLevel%% neq 0 ( >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo     echo ERROR: Administrator privileges required! >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo     pause >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo     exit /b 1 >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo ^) >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo echo [1/5] Stopping Display Control+ processes... >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo taskkill /f /im DisplayControlPlus.exe ^>nul 2^>^&1 >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo echo [2/5] Removing scheduled task... >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo schtasks /delete /tn "DisplayControlPlus_Background" /f ^>nul 2^>^&1 >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo echo [3/5] Removing shortcuts... >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo del "%%USERPROFILE%%\Desktop\Display Control+.lnk" ^>nul 2^>^&1 >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo rmdir /s /q "%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\Display Control Plus" ^>nul 2^>^&1 >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo echo [4/5] Removing application files... >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo rmdir /s /q "C:\Program Files\DisplayControlPlus" ^>nul 2^>^&1 >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo echo [5/5] Cleanup complete! >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo echo. >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo echo Display Control+ has been completely removed. >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"
echo pause >> "DisplayControlPlus_Production\Professional_Uninstaller.bat"

REM Copy documentation
echo [7/8] Creating documentation...
echo # Display Control+ Professional Edition > "DisplayControlPlus_Production\Documentation\README.txt"
echo. >> "DisplayControlPlus_Production\Documentation\README.txt"
echo ## OLED Screen Protection Software >> "DisplayControlPlus_Production\Documentation\README.txt"
echo. >> "DisplayControlPlus_Production\Documentation\README.txt"
echo ### What it does: >> "DisplayControlPlus_Production\Documentation\README.txt"
echo - Automatically protects OLED screens from burn-in >> "DisplayControlPlus_Production\Documentation\README.txt"
echo - Detects when you're away and displays protective overlays >> "DisplayControlPlus_Production\Documentation\README.txt"
echo - Multiple protection modes: blank screen, images, slideshows >> "DisplayControlPlus_Production\Documentation\README.txt"
echo - Configurable timeout and detection settings >> "DisplayControlPlus_Production\Documentation\README.txt"
echo - Runs silently in background >> "DisplayControlPlus_Production\Documentation\README.txt"
echo. >> "DisplayControlPlus_Production\Documentation\README.txt"
echo ### Installation: >> "DisplayControlPlus_Production\Documentation\README.txt"
echo 1. Right-click Professional_Installer.bat >> "DisplayControlPlus_Production\Documentation\README.txt"
echo 2. Select "Run as administrator" >> "DisplayControlPlus_Production\Documentation\README.txt"
echo 3. Follow the installation prompts >> "DisplayControlPlus_Production\Documentation\README.txt"
echo 4. Use the desktop shortcut to configure settings >> "DisplayControlPlus_Production\Documentation\README.txt"
echo. >> "DisplayControlPlus_Production\Documentation\README.txt"
echo ### System Requirements: >> "DisplayControlPlus_Production\Documentation\README.txt"
echo - Windows 10 or Windows 11 >> "DisplayControlPlus_Production\Documentation\README.txt"
echo - Administrator privileges for installation >> "DisplayControlPlus_Production\Documentation\README.txt"
echo - OLED or other burn-in susceptible display >> "DisplayControlPlus_Production\Documentation\README.txt"
echo. >> "DisplayControlPlus_Production\Documentation\README.txt"
echo ### Support: >> "DisplayControlPlus_Production\Documentation\README.txt"
echo For technical support or questions, please contact support. >> "DisplayControlPlus_Production\Documentation\README.txt"

REM Create license file
echo Display Control+ Professional Edition > "DisplayControlPlus_Production\Documentation\LICENSE.txt"
echo Copyright (c) 2025. All rights reserved. >> "DisplayControlPlus_Production\Documentation\LICENSE.txt"
echo. >> "DisplayControlPlus_Production\Documentation\LICENSE.txt"
echo This software is licensed for personal and commercial use. >> "DisplayControlPlus_Production\Documentation\LICENSE.txt"
echo Redistribution is prohibited without written permission. >> "DisplayControlPlus_Production\Documentation\LICENSE.txt"

REM Create the final ZIP package
echo [8/8] Creating final distribution package...
powershell -Command "Compress-Archive -Path 'DisplayControlPlus_Production\*' -DestinationPath 'DisplayControlPlus_Production.zip' -Force"

echo.
echo ===============================================
echo     Production Package Created Successfully!
echo ===============================================
echo.
echo File: DisplayControlPlus_Production.zip
echo Size: 
dir "DisplayControlPlus_Production.zip" | find "DisplayControlPlus_Production.zip"
echo.
echo This package is now ready for commercial distribution!
echo.
pause
