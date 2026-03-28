# Co-Op OS One-Click Installer (Windows)
# -------------------------------------

$ErrorActionPreference = "Stop"

# Configurable variables via environment
$InstallDir = if ($env:COOP_INSTALL_DIR) { $env:COOP_INSTALL_DIR } else { "$HOME\.co-op" }
$ComposeUrl = if ($env:COOP_COMPOSE_URL) { $env:COOP_COMPOSE_URL } else { "https://raw.githubusercontent.com/NAVANEETHVVINOD/CO_OP/main/infrastructure/docker/docker-compose.yml" }
$EnvExampleUrl = if ($env:COOP_ENV_EXAMPLE_URL) { $env:COOP_ENV_EXAMPLE_URL } else { "https://raw.githubusercontent.com/NAVANEETHVVINOD/CO_OP/main/infrastructure/docker/.env.example" }

Write-Host "🚀 Starting Co-Op Autonomous Company OS Installer..." -ForegroundColor Cyan
Write-Host "Install directory: $InstallDir" -ForegroundColor Cyan
Write-Host ""

# 1. Dependency Checks
Write-Host "🔍 Checking dependencies..." -ForegroundColor White

# Check Docker
try {
    $dockerVer = docker --version
    Write-Host "✅ Docker found: $dockerVer" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed." -ForegroundColor Red
    Write-Host "Please install Docker Desktop for Windows and try again." -ForegroundColor Red
    Write-Host "Visit: https://docs.docker.com/desktop/install/windows-install/" -ForegroundColor Yellow
    exit 1
}

# Check Docker Compose
try {
    $composeVer = docker compose version
    Write-Host "✅ Docker Compose found: $composeVer" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not available." -ForegroundColor Red
    Write-Host "Please ensure Docker Desktop is properly installed." -ForegroundColor Red
    exit 1
}

# 2. Create installation directory
Write-Host "`n📁 Creating installation directory..." -ForegroundColor White
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Set-Location $InstallDir
Write-Host "✅ Installation directory created: $InstallDir" -ForegroundColor Green

# 3. Download configuration files
Write-Host "`n⬇️  Downloading configuration files..." -ForegroundColor White

Write-Host "Downloading docker-compose.yml..." -ForegroundColor Gray
try {
    Invoke-WebRequest -Uri $ComposeUrl -OutFile "docker-compose.yml" -ErrorAction Stop
    Write-Host "✅ docker-compose.yml downloaded" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to download docker-compose.yml" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Downloading .env.example..." -ForegroundColor Gray
try {
    Invoke-WebRequest -Uri $EnvExampleUrl -OutFile ".env.example" -ErrorAction Stop
    Write-Host "✅ .env.example downloaded" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to download .env.example" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

# 4. Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "`n📝 Creating .env file from .env.example..." -ForegroundColor White
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: You must edit the .env file before starting services!" -ForegroundColor Yellow
    Write-Host "   Edit: $InstallDir\.env" -ForegroundColor Yellow
    Write-Host "   Set your passwords, API keys, and other configuration values." -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "`n✅ .env file already exists" -ForegroundColor Green
}

# 5. Installation complete
Write-Host "`n✨ Installation Complete! ✨" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Edit your configuration: $InstallDir\.env" -ForegroundColor Cyan
Write-Host "  2. Start the services: cd $InstallDir; docker compose up -d" -ForegroundColor Cyan
Write-Host "  3. Access the UI: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "For more information, visit: https://github.com/NAVANEETHVVINOD/CO_OP" -ForegroundColor White
Write-Host ""
