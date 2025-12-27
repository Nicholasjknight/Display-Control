@echo off
REM Display Control+ Build Script
REM Creates a standalone .exe for distribution

echo.
echo ========================================
echo Display Control+ Build System
echo ========================================
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
)

REM Build the executable
echo.
echo Building Display Control+.exe...
echo.

pyinstaller DisplayControl.spec

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Build successful!
    echo.
    echo Your executable is ready at:
    echo   dist\DisplayControl+.exe
    echo.
    echo You can now:
    echo   1. Run it directly: dist\DisplayControl+.exe
    echo   2. Distribute it to users
    echo   3. Create an installer (optional)
    echo.
) else (
    echo.
    echo ✗ Build failed. Check the output above for errors.
    echo.
)

pause
