@echo off
REM Create a self-extracting archive that auto-starts the installer
title Creating Self-Extracting Display Control+ Package

echo.
echo ===============================================
echo   Creating Self-Extracting Package
echo ===============================================
echo.

REM Update the distribution with new files
echo Updating distribution package...
copy /Y "Complete_Cleanup.bat" "DisplayControlPlus_Distribution\" >nul
copy /Y "AutoSetup.bat" "DisplayControlPlus_Distribution\" >nul

REM Update README with cleanup instructions
(
echo Display Control+ - OLED Screen Protector
echo ========================================
echo.
echo IMPORTANT - FIRST TIME INSTALLATION:
echo If you have any previous Display Control+ versions installed,
echo run "Complete_Cleanup.bat" as administrator first to avoid conflicts.
echo.
echo QUICK INSTALLATION:
echo 1. Run "AutoSetup.bat" as administrator for automatic setup
echo 2. Follow the on-screen instructions
echo 3. Double-click the desktop shortcut to configure
echo.
echo MANUAL INSTALLATION:
echo 1. Run "DisplayControlPlus_Installer.bat" as administrator
echo 2. Follow the on-screen instructions
echo 3. Double-click the desktop shortcut to configure
echo.
echo CLEANUP TOOL:
echo - Run "Complete_Cleanup.bat" to remove all installations
echo - Use "Uninstaller.bat" to remove current installation only
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

echo Creating new distribution ZIP...
if exist "DisplayControlPlus_v1.1.zip" del "DisplayControlPlus_v1.1.zip"
powershell -Command "Compress-Archive -Path 'DisplayControlPlus_Distribution\*' -DestinationPath 'DisplayControlPlus_v1.1.zip' -Force"

echo.
echo ===============================================
echo     Self-Extracting Package Created!
echo ===============================================
echo.
echo Package: DisplayControlPlus_v1.1.zip
echo.
echo New features:
echo  - Complete_Cleanup.bat ^(removes all previous installations^)
echo  - AutoSetup.bat ^(automatic installation^)
echo  - Enhanced conflict detection
echo  - Improved user instructions
echo.
echo Ready for distribution!
echo.
pause
