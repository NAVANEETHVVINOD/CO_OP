# Run Desktop App - PowerShell Script
# This script ensures Rust/Cargo is in PATH before running the desktop app

Write-Host "Co-Op Desktop App Launcher" -ForegroundColor Cyan
Write-Host "============================`n" -ForegroundColor Cyan

# Add Rust to PATH for this session
$env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"

# Verify Rust is available
Write-Host "Checking Rust installation..." -ForegroundColor Yellow
try {
    $rustVersion = cargo --version
    Write-Host "✓ Rust found: $rustVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Rust not found!" -ForegroundColor Red
    Write-Host "`nPlease install Rust from: https://rustup.rs/" -ForegroundColor Yellow
    Write-Host "After installation, restart your terminal and try again.`n" -ForegroundColor Yellow
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "package.json")) {
    Write-Host "✗ Error: Not in desktop app directory!" -ForegroundColor Red
    Write-Host "Please run this script from: apps/desktop/`n" -ForegroundColor Yellow
    exit 1
}

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
    pnpm install
}

# Run the desktop app
Write-Host "`nStarting desktop app..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Gray

pnpm tauri dev
