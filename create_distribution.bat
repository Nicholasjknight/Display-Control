@echo off
title Create Display Control+ Distribution Package
color 0B

echo.
echo ===============================================
echo   Creating Display Control+ Distribution
echo ===============================================
echo.

REM Create distribution directory
if exist "DisplayControlPlus_Distribution" rmdir /s /q "DisplayControlPlus_Distribution"
mkdir "DisplayControlPlus_Distribution"

echo Copying installer files...
REM Copy the built executable and all dependencies
xcopy /E /I /Y "installer\dist\DisplayControlPlus" "DisplayControlPlus_Distribution\DisplayControlPlus\"

echo Copying configuration and assets...
REM Copy essential files
copy /Y "config.json" "DisplayControlPlus_Distribution\" >nul
copy /Y "Display Control+ Logo.png" "DisplayControlPlus_Distribution\" >nul
if exist "installer\Display Control+ Logo.ico" copy /Y "installer\Display Control+ Logo.ico" "DisplayControlPlus_Distribution\" >nul
copy /Y "DisplayControlPlus_Installer.bat" "DisplayControlPlus_Distribution\" >nul

echo Creating documentation...
REM Create README for users
(
echo Display Control+ - OLED Screen Protector
echo ========================================
echo.
echo INSTALLATION:
echo 1. Run DisplayControlPlus_Installer.bat as administrator
echo 2. Follow the on-screen instructions
echo 3. Double-click the desktop shortcut to configure
echo.
echo FEATURES:
echo - Automatic idle detection
echo - Customizable overlay modes ^(blank, image, slideshow, GIF^)
echo - Per-monitor or system-wide protection
echo - Windows startup integration
echo - Prevention of OLED burn-in and pixel degradation
echo.
echo USAGE:
echo 1. Set your preferred idle timeout
echo 2. Choose overlay type
echo 3. Click 'Apply' to activate
echo 4. Test with 'Test Overlay' buttons
echo.
echo The background service runs automatically and monitors
echo for inactivity. When detected, protective overlays are
echo displayed until you move the mouse or press a key.
echo.
echo For support or updates, check the project repository.
) > "DisplayControlPlus_Distribution\README.txt"

REM Create uninstaller
(
echo @echo off
echo title Display Control+ Uninstaller
echo.
echo Removing Display Control+...
echo.
echo Stopping background service...
echo powershell -Command "try { Unregister-ScheduledTask -TaskName 'DisplayControlPlus_Background' -Confirm:$false } catch { Write-Host 'Background service not found' }"
echo.
echo Removing desktop shortcut...
echo if exist "%%USERPROFILE%%\Desktop\Display Control+.lnk" del "%%USERPROFILE%%\Desktop\Display Control+.lnk"
echo.
echo Removing application files...
echo if exist "%%APPDATA%%\DisplayControlPlus" rmdir /s /q "%%APPDATA%%\DisplayControlPlus"
echo.
echo Display Control+ has been removed from your system.
echo.
echo pause
) > "DisplayControlPlus_Distribution\Uninstaller.bat"

echo.
echo ===============================================
echo     Distribution Package Created!
echo ===============================================
echo.
echo Package location: DisplayControlPlus_Distribution\
echo.
echo Contents:
echo  - DisplayControlPlus\ ^(application files^)
echo  - DisplayControlPlus_Installer.bat ^(installer^)
echo  - Uninstaller.bat ^(removal tool^)
echo  - README.txt ^(user instructions^)
echo  - config.json ^(default settings^)
echo  - Display Control+ Logo.png ^(icon^)
echo.
echo Ready for distribution!
echo.
pause
