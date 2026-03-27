# ============================================================================
# Co-Op OS v1.0.3 Environment Validation Script (PowerShell)
# ============================================================================

param([string]$EnvFile = "")

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrEmpty($EnvFile)) {
    $EnvFile = Join-Path $ScriptDir ".env"
}

Write-Host "Co-Op OS v1.0.3 - Environment Validation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $EnvFile)) {
    Write-Host "Error: Environment file not found: $EnvFile" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create a .env file from .env.example:"
    Write-Host "  Copy-Item $ScriptDir\.env.example $ScriptDir\.env"
    Write-Host ""
    exit 1
}

Write-Host "Found environment file: $EnvFile" -ForegroundColor Green
Write-Host ""

$RequiredVars = @(
    "DB_PASS",
    "MINIO_ROOT_USER",
    "MINIO_ROOT_PASSWORD",
    "SECRET_KEY",
    "OLLAMA_URL",
    "API_BASE_URL",
    "FRONTEND_URL",
    "LITELLM_URL",
    "REDIS_URL",
    "MINIO_URL",
    "ENVIRONMENT",
    "NEXT_PUBLIC_API_URL"
)

$EnvVars = @{}
Get-Content $EnvFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith('#')) {
        if ($line -match '^([^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            $EnvVars[$key] = $value
        }
    }
}

$Missing = @()
foreach ($var in $RequiredVars) {
    if (-not $EnvVars.ContainsKey($var) -or [string]::IsNullOrEmpty($EnvVars[$var])) {
        $Missing += $var
    }
}

if ($Missing.Count -gt 0) {
    Write-Host "Error: Missing required environment variables:" -ForegroundColor Red
    Write-Host ""
    foreach ($var in $Missing) {
        Write-Host "  - $var" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "Please set these variables in $EnvFile"
    Write-Host "Refer to $ScriptDir\.env.example for guidance"
    Write-Host ""
    exit 1
}

$SecretKey = $EnvVars["SECRET_KEY"]
if ($SecretKey.Length -lt 32) {
    Write-Host "Error: SECRET_KEY must be at least 32 characters long" -ForegroundColor Red
    Write-Host "   Current length: $($SecretKey.Length)"
    Write-Host ""
    Write-Host "Please update SECRET_KEY in $EnvFile"
    Write-Host ""
    exit 1
}

$Environment = $EnvVars["ENVIRONMENT"]
$validEnvs = @("development", "staging", "production")
if ($validEnvs -notcontains $Environment) {
    Write-Host "Warning: ENVIRONMENT should be one of: development, staging, production" -ForegroundColor Yellow
    Write-Host "   Current value: $Environment"
    Write-Host ""
}

Write-Host "All required environment variables are set" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration summary:"
Write-Host "  Environment:     $($EnvVars['ENVIRONMENT'])"
if ($EnvVars.ContainsKey('DATABASE_URL')) {
    $dbParts = $EnvVars['DATABASE_URL'] -split '@'
    if ($dbParts.Count -gt 1) {
        Write-Host "  Database:        $($dbParts[0])@***"
    }
}
Write-Host "  Redis:           $($EnvVars['REDIS_URL'])"
Write-Host "  MinIO:           $($EnvVars['MINIO_URL'])"
Write-Host "  API URL:         $($EnvVars['API_BASE_URL'])"
Write-Host "  Frontend URL:    $($EnvVars['FRONTEND_URL'])"
Write-Host "  Public API URL:  $($EnvVars['NEXT_PUBLIC_API_URL'])"
Write-Host ""
Write-Host "Ready to start Docker services" -ForegroundColor Green
Write-Host ""
