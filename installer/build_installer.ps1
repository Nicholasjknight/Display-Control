# PowerShell script to automate building and packaging OLED Protector
# 1. Build standalone .exe with PyInstaller
# 2. Build installer with Inno Setup
# 3. Output ready-to-distribute installer

param(
    [string]$ProjectRoot = "$PSScriptRoot\.."
)

$ErrorActionPreference = 'Stop'

# Step 1: Build with PyInstaller
Write-Host "[1/3] Building standalone executable with PyInstaller..."
$pyinstaller = "pyinstaller"
$specFile = "$PSScriptRoot\pyinstaller.spec"
Push-Location $ProjectRoot
try {
    & $pyinstaller --noconfirm --clean --onefile --windowed --distpath "$ProjectRoot\dist" "$specFile"
} catch {
    Write-Error "PyInstaller build failed: $_"
    exit 1
}
Pop-Location

# Step 2: Build installer with Inno Setup
Write-Host "[2/3] Building installer with Inno Setup..."
$innoSetup = "ISCC.exe"
$issFile = "$PSScriptRoot\OLEDProtector.iss"
try {
    & $innoSetup "$issFile"
} catch {
    Write-Error "Inno Setup build failed: $_"
    exit 1
}

# Step 3: Output result
Write-Host "[3/3] Build complete! Installer is in $ProjectRoot\OLEDProtectorSetup.exe"
