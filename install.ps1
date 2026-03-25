# Co-Op OS One-Click Installer (Windows)
# -------------------------------------

$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting Co-Op Autonomous Company OS Installer..." -ForegroundColor Cyan

# 1. Dependency Checks
Write-Host "`n🔍 Checking dependencies..."

# Check Docker
try {
    $dockerVer = docker --version
    Write-Host "✅ Docker found: $dockerVer" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop for Windows and try again." -ForegroundColor Red
    exit
}

# Check Python
try {
    $pythonVer = python --version
    Write-Host "✅ Python found: $pythonVer" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed. Please install Python 3.10+ and try again." -ForegroundColor Red
    exit
}

# 2. Install CLI
Write-Host "`n🛠️ Installing Co-Op CLI..." -ForegroundColor Yellow
pip install -e .\cli

# 3. Onboarding
Write-Host "`n🌟 Starting Onboarding Wizard..." -ForegroundColor Cyan
coop onboard setup

# 4. Startup Shortcut
Write-Host "`n📁 Adding Co-Op to Startup..." -ForegroundColor Yellow
$WshShell = New-Object -ComObject WScript.Shell
$ShortcutPath = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup\CoOp-Gateway.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-Command `"coop gateway start`""
$Shortcut.WindowStyle = 7 # Minimized
$Shortcut.Save()

Write-Host "`n✨ Installation Complete! ✨" -ForegroundColor Green
Write-Host "You can now run 'coop gateway start' to launch the system." -ForegroundColor White
