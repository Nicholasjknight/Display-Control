@echo off
title Display Control+ - Simple Setup
color 07
cls
echo.
echo ===============================================
echo          Display Control+ Setup
echo    OLED Screen Protection Software
echo ===============================================
echo.
echo This will:
echo  1. Install Display Control+ to your computer
echo  2. Create a desktop shortcut
echo  3. Start background OLED protection
echo.
echo Press any key to continue...
pause >nul
echo.

REM Check admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run as administrator!
    echo Right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo Installing Display Control+...
echo.

REM Check if ZIP file exists
if not exist "%~dp0DisplayControlPlus_Production.zip" (
    echo ERROR: DisplayControlPlus_Production.zip not found!
    echo Make sure this file is in the same folder as the setup.
    echo.
    pause
    exit /b 1
)

echo [1/5] Creating install directory...
if not exist "C:\Program Files\DisplayControlPlus" mkdir "C:\Program Files\DisplayControlPlus"
if %errorLevel% neq 0 (
    echo ERROR: Could not create install directory!
    pause
    exit /b 1
)

echo [2/5] Extracting files...
powershell -Command "try { Expand-Archive -Path '%~dp0DisplayControlPlus_Production.zip' -DestinationPath '%TEMP%\DisplayControlSetup' -Force; Write-Host 'Extraction successful' } catch { Write-Host 'Extraction failed:' $_.Exception.Message; exit 1 }"
if %errorLevel% neq 0 (
    echo ERROR: Could not extract files!
    pause
    exit /b 1
)

echo [3/5] Copying application files...
if exist "%TEMP%\DisplayControlSetup\Application" (
    xcopy "%TEMP%\DisplayControlSetup\Application\*" "C:\Program Files\DisplayControlPlus\" /E /I /Y >nul
    if %errorLevel% neq 0 (
        echo ERROR: Could not copy application files!
        pause
        exit /b 1
    )
) else (
    echo ERROR: Application folder not found in ZIP!
    dir "%TEMP%\DisplayControlSetup"
    pause
    exit /b 1
)

echo [4/5] Creating desktop shortcut...
powershell -Command "try { $WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Display Control+.lnk'); $Shortcut.TargetPath = 'C:\Program Files\DisplayControlPlus\DisplayControlPlus.exe'; $Shortcut.WorkingDirectory = 'C:\Program Files\DisplayControlPlus'; $Shortcut.Save(); Write-Host 'Shortcut created' } catch { Write-Host 'Shortcut failed:' $_.Exception.Message }"

echo [5/5] Starting background service...
if exist "C:\Program Files\DisplayControlPlus\DisplayControlPlus.exe" (
    start /B "DisplayControlPlus" "C:\Program Files\DisplayControlPlus\DisplayControlPlus.exe" --background
    echo Background service started
) else (
    echo WARNING: DisplayControlPlus.exe not found at expected location!
    dir "C:\Program Files\DisplayControlPlus"
)

echo.
echo [Cleanup] Removing temporary files...
rmdir /s /q "%TEMP%\DisplayControlSetup" 2>nul

echo.
echo ===============================================
echo         Installation Complete!
echo ===============================================
echo.
echo Display Control+ has been installed successfully!
echo.
echo - Desktop shortcut created: "Display Control+"
echo - Background protection is now running
echo - Click the desktop shortcut to configure settings
echo.
echo Your OLED screen is now protected!
echo.
pause
