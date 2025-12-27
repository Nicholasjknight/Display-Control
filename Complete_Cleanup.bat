@echo off
title Display Control+ Complete Cleanup
color 0C

echo.
echo =============================================
echo     Display Control+ Complete Cleanup
echo =============================================
echo.
echo This will remove ALL Display Control+ installations
echo and clean up scheduled tasks, processes, and files.
echo.
pause

echo.
echo [1/6] Stopping all Display Control+ processes...
taskkill /f /im "DisplayControlPlus.exe" 2>nul
taskkill /f /im "overlay_bg.exe" 2>nul
taskkill /f /im "python.exe" 2>nul
echo Done.

echo.
echo [2/6] Removing scheduled tasks...
schtasks /delete /tn "DisplayControlPlus_Background" /f 2>nul
schtasks /delete /tn "OLED_Protector_Background" /f 2>nul
schtasks /delete /tn "Display Control+ Background" /f 2>nul
echo Done.

echo.
echo [3/6] Removing desktop shortcuts...
del "%USERPROFILE%\Desktop\Display Control+.lnk" 2>nul
del "%USERPROFILE%\Desktop\DisplayControlPlus.lnk" 2>nul
del "%USERPROFILE%\Desktop\OLED Protector.lnk" 2>nul
del "%PUBLIC%\Desktop\Display Control+.lnk" 2>nul
del "%PUBLIC%\Desktop\DisplayControlPlus.lnk" 2>nul
echo Done.

echo.
echo [4/6] Removing Start Menu shortcuts...
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Display Control+.lnk" 2>nul
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\DisplayControlPlus.lnk" 2>nul
echo Done.

echo.
echo [5/6] Removing application directories...
if exist "%APPDATA%\DisplayControlPlus" (
    echo Removing "%APPDATA%\DisplayControlPlus"...
    rmdir /s /q "%APPDATA%\DisplayControlPlus"
)
if exist "%APPDATA%\Display Control+" (
    echo Removing "%APPDATA%\Display Control+"...
    rmdir /s /q "%APPDATA%\Display Control+"
)
if exist "%PROGRAMFILES%\DisplayControlPlus" (
    echo Removing "%PROGRAMFILES%\DisplayControlPlus"...
    rmdir /s /q "%PROGRAMFILES%\DisplayControlPlus"
)
if exist "%PROGRAMFILES(X86)%\DisplayControlPlus" (
    echo Removing "%PROGRAMFILES(X86)%\DisplayControlPlus"...
    rmdir /s /q "%PROGRAMFILES(X86)%\DisplayControlPlus"
)
echo Done.

echo.
echo [6/6] Cleaning registry entries (if any)...
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DisplayControlPlus" /f 2>nul
reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "DisplayControlPlus" /f 2>nul
echo Done.

echo.
echo =============================================
echo    Complete Cleanup Finished!
echo =============================================
echo.
echo All Display Control+ installations have been removed.
echo You can now safely install a fresh copy.
echo.
pause
