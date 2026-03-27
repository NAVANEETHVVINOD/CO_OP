# Co-Op OS v1.0.3 - Security Scan Script (PowerShell)
# Scans for security issues in the codebase

param([switch]$Verbose)

Write-Host "Co-Op OS v1.0.3 - Security Scan" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$Errors = 0
$Warnings = 0

# Check 1: Hardcoded secrets in Python files
Write-Host "Checking for hardcoded secrets in Python files..." -ForegroundColor Yellow
Write-Host ""

$SecretPatterns = @(
    'password\s*=\s*[''"][^''"]+[''"]',
    'api_key\s*=\s*[''"][^''"]+[''"]',
    'secret\s*=\s*[''"][^''"]+[''"]',
    'token\s*=\s*[''"][^''"]+[''"]',
    'SECRET_KEY\s*=\s*[''"][^''"]+[''"]'
)

foreach ($pattern in $SecretPatterns) {
    $matches = Get-ChildItem -Path "services/api/app" -Filter "*.py" -Recurse -ErrorAction SilentlyContinue |
        Select-String -Pattern $pattern |
        Where-Object { $_.Line -notmatch "test_" -and $_.Line -notmatch "os\.getenv" -and $_.Line -notmatch "settings\." }
    
    if ($matches) {
        Write-Host "ERROR: Found potential hardcoded secret:" -ForegroundColor Red
        $matches | ForEach-Object { Write-Host "  $($_.Path):$($_.LineNumber): $($_.Line)" }
        $Errors++
    }
}

# Check 2: Hardcoded secrets in TypeScript files
Write-Host "Checking for hardcoded secrets in TypeScript files..." -ForegroundColor Yellow
Write-Host ""

$TsSecretPatterns = @(
    'password:\s*[''"][^''"]+[''"]',
    'apiKey:\s*[''"][^''"]+[''"]',
    'secret:\s*[''"][^''"]+[''"]',
    'token:\s*[''"][^''"]+[''"]'
)

foreach ($pattern in $TsSecretPatterns) {
    $matches = Get-ChildItem -Path "apps/web/src" -Include "*.ts","*.tsx" -Recurse -ErrorAction SilentlyContinue |
        Select-String -Pattern $pattern |
        Where-Object { $_.Line -notmatch "test" -and $_.Line -notmatch "process\.env" -and $_.Line -notmatch "env\." }
    
    if ($matches) {
        Write-Host "ERROR: Found potential hardcoded secret:" -ForegroundColor Red
        $matches | ForEach-Object { Write-Host "  $($_.Path):$($_.LineNumber): $($_.Line)" }
        $Errors++
    }
}

# Check 3: .env files in version control
Write-Host "Checking for .env files in version control..." -ForegroundColor Yellow
Write-Host ""

$EnvFiles = git ls-files | Where-Object { $_ -match '\.env$' -and $_ -notmatch '\.env\.example' -and $_ -notmatch '\.env\.template' }
if ($EnvFiles) {
    Write-Host "ERROR: Found .env files in version control:" -ForegroundColor Red
    $EnvFiles | ForEach-Object { Write-Host "  $_" }
    $Errors++
} else {
    Write-Host "SUCCESS: No .env files in version control" -ForegroundColor Green
}
Write-Host ""

# Check 4: .gitignore includes .env patterns
Write-Host "Checking .gitignore for .env patterns..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path ".gitignore") {
    $gitignoreContent = Get-Content ".gitignore"
    if ($gitignoreContent -match '\.env') {
        Write-Host "SUCCESS: .gitignore includes .env patterns" -ForegroundColor Green
    } else {
        Write-Host "ERROR: .gitignore does not include .env patterns" -ForegroundColor Red
        $Errors++
    }
} else {
    Write-Host "ERROR: .gitignore file not found" -ForegroundColor Red
    $Errors++
}
Write-Host ""

# Check 5: Hardcoded URLs in Python files
Write-Host "Checking for hardcoded URLs in Python files..." -ForegroundColor Yellow
Write-Host ""

$UrlPatterns = @(
    'http://localhost:\d+',
    'http://127\.0\.0\.1:\d+'
)

foreach ($pattern in $UrlPatterns) {
    $matches = Get-ChildItem -Path "services/api/app" -Filter "*.py" -Recurse -ErrorAction SilentlyContinue |
        Select-String -Pattern $pattern |
        Where-Object { $_.Line -notmatch "#" -and $_.Line -notmatch "test_" -and $_.Line -notmatch "settings\." -and $_.Line -notmatch "os\.getenv" }
    
    if ($matches) {
        Write-Host "WARNING: Found hardcoded URL (should use settings):" -ForegroundColor Yellow
        $matches | ForEach-Object { Write-Host "  $($_.Path):$($_.LineNumber): $($_.Line)" }
        $Warnings++
    }
}

# Check 6: Hardcoded URLs in TypeScript files
Write-Host "Checking for hardcoded URLs in TypeScript files..." -ForegroundColor Yellow
Write-Host ""

foreach ($pattern in $UrlPatterns) {
    $matches = Get-ChildItem -Path "apps/web/src" -Include "*.ts","*.tsx" -Recurse -ErrorAction SilentlyContinue |
        Select-String -Pattern $pattern |
        Where-Object { $_.Line -notmatch "//" -and $_.Line -notmatch "process\.env" -and $_.Line -notmatch "env\." }
    
    if ($matches) {
        Write-Host "WARNING: Found hardcoded URL (should use env):" -ForegroundColor Yellow
        $matches | ForEach-Object { Write-Host "  $($_.Path):$($_.LineNumber): $($_.Line)" }
        $Warnings++
    }
}

# Summary
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Security Scan Summary" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

if ($Errors -eq 0 -and $Warnings -eq 0) {
    Write-Host "All security checks passed!" -ForegroundColor Green
    Write-Host ""
    exit 0
} elseif ($Errors -eq 0) {
    Write-Host "Security scan completed with $Warnings warning(s)" -ForegroundColor Yellow
    Write-Host ""
    exit 0
} else {
    Write-Host "Security scan failed with $Errors error(s) and $Warnings warning(s)" -ForegroundColor Red
    Write-Host ""
    exit 1
}
