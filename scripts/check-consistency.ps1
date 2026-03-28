# ============================================================================
# Co-Op OS v1.0.3 Configuration Consistency Check Script (PowerShell)
# ============================================================================

param([switch]$Verbose)

Write-Host "Co-Op OS v1.0.3 - Configuration Consistency Check" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

$Errors = 0
$Warnings = 0

# ============================================================================
# Extract Environment Variables from Different Sources
# ============================================================================

Write-Host "Extracting environment variables from configuration files..." -ForegroundColor Yellow
Write-Host ""

# Extract from docker-compose.yml
$ComposeFile = "infrastructure/docker/docker-compose.yml"
if (Test-Path $ComposeFile) {
    $composeContent = Get-Content $ComposeFile -Raw
    $ComposeVars = [regex]::Matches($composeContent, '\$\{([A-Z_][A-Z0-9_]+)[:-]?') | 
        ForEach-Object { $_.Groups[1].Value } | 
        Select-Object -Unique | 
        Sort-Object
    Write-Host "  Found $($ComposeVars.Count) variables in docker-compose.yml" -ForegroundColor Green
} else {
    Write-Host "  docker-compose.yml not found at $ComposeFile" -ForegroundColor Red
    $Errors++
    exit 1
}

# Extract from Backend Settings (config.py)
$ConfigFile = "services/api/app/config.py"
if (Test-Path $ConfigFile) {
    $configContent = Get-Content $ConfigFile -Raw
    $BackendVars = [regex]::Matches($configContent, '^\s+([A-Z_][A-Z0-9_]+):', [System.Text.RegularExpressions.RegexOptions]::Multiline) | 
        ForEach-Object { $_.Groups[1].Value } | 
        Where-Object { $_ -notmatch '^(model_config|VERSION)$' } |
        Select-Object -Unique | 
        Sort-Object
    Write-Host "  Found $($BackendVars.Count) variables in Backend Settings" -ForegroundColor Green
} else {
    Write-Host "  config.py not found at $ConfigFile" -ForegroundColor Red
    $Errors++
}

# Extract from Frontend env module (env.ts)
$EnvTsFile = "apps/web/src/lib/env.ts"
if (Test-Path $EnvTsFile) {
    $envTsContent = Get-Content $EnvTsFile -Raw
    $FrontendVars = [regex]::Matches($envTsContent, 'process\.env\.([A-Z_][A-Z0-9_]+)') | 
        ForEach-Object { $_.Groups[1].Value } | 
        Select-Object -Unique | 
        Sort-Object
    Write-Host "  Found $($FrontendVars.Count) variables in Frontend env module" -ForegroundColor Green
} else {
    Write-Host "  env.ts not found at $EnvTsFile (may not be created yet)" -ForegroundColor Yellow
    $FrontendVars = @()
    $Warnings++
}

# Extract from .env.example
$EnvExample = "infrastructure/docker/.env.example"
if (Test-Path $EnvExample) {
    $ExampleVars = Get-Content $EnvExample | 
        Where-Object { $_ -match '^[A-Z_][A-Z0-9_]+=' } | 
        ForEach-Object { ($_ -split '=')[0] } | 
        Select-Object -Unique | 
        Sort-Object
    Write-Host "  Found $($ExampleVars.Count) variables in .env.example" -ForegroundColor Green
} else {
    Write-Host "  .env.example not found at $EnvExample" -ForegroundColor Red
    $Errors++
    exit 1
}

Write-Host ""

# ============================================================================
# Check 1: Docker Compose Variables in .env.example
# ============================================================================
Write-Host "Checking docker-compose.yml variables are in .env.example..." -ForegroundColor Yellow
Write-Host ""

$MissingInExample = 0
foreach ($var in $ComposeVars) {
    if ($ExampleVars -notcontains $var) {
        Write-Host "  $var used in docker-compose.yml but not in .env.example" -ForegroundColor Red
        $MissingInExample++
        $Errors++
    }
}

if ($MissingInExample -eq 0) {
    Write-Host "  All docker-compose.yml variables are in .env.example" -ForegroundColor Green
}
Write-Host ""

# ============================================================================
# Check 2: Backend Settings Variables in .env.example
# ============================================================================
Write-Host "Checking Backend Settings variables are in .env.example..." -ForegroundColor Yellow
Write-Host ""

$MissingBackend = 0
foreach ($var in $BackendVars) {
    if ($ExampleVars -notcontains $var) {
        Write-Host "  $var in Backend Settings but not in .env.example" -ForegroundColor Red
        $MissingBackend++
        $Errors++
    }
}

if ($MissingBackend -eq 0) {
    Write-Host "  All Backend Settings variables are in .env.example" -ForegroundColor Green
}
Write-Host ""

# ============================================================================
# Check 3: Frontend Variables in .env.example
# ============================================================================
if ($FrontendVars.Count -gt 0) {
    Write-Host "Checking Frontend env variables are in .env.example..." -ForegroundColor Yellow
    Write-Host ""
    
    $MissingFrontend = 0
    foreach ($var in $FrontendVars) {
        if ($ExampleVars -notcontains $var) {
            Write-Host "  $var in Frontend env module but not in .env.example" -ForegroundColor Red
            $MissingFrontend++
            $Errors++
        }
    }
    
    if ($MissingFrontend -eq 0) {
        Write-Host "  All Frontend env variables are in .env.example" -ForegroundColor Green
    }
    Write-Host ""
}

# ============================================================================
# Check 4: Required Variables for Production
# ============================================================================
Write-Host "Checking required variables for production..." -ForegroundColor Yellow
Write-Host ""

$RequiredProdVars = @(
    "DB_PASS",
    "SECRET_KEY",
    "MINIO_ROOT_USER",
    "MINIO_ROOT_PASSWORD",
    "OLLAMA_URL",
    "API_BASE_URL",
    "FRONTEND_URL",
    "NEXT_PUBLIC_API_URL"
)

$MissingRequired = 0
foreach ($var in $RequiredProdVars) {
    if ($ExampleVars -notcontains $var) {
        Write-Host "  Required production variable $var not in .env.example" -ForegroundColor Red
        $MissingRequired++
        $Errors++
    }
}

if ($MissingRequired -eq 0) {
    Write-Host "  All required production variables are documented" -ForegroundColor Green
}
Write-Host ""

# ============================================================================
# Check 5: Conflicting Default Values
# ============================================================================
Write-Host "Checking for conflicting default values..." -ForegroundColor Yellow
Write-Host ""

$composeContent = Get-Content $ComposeFile -Raw
$ComposeDefaults = [regex]::Matches($composeContent, '\$\{[A-Z_][A-Z0-9_]+:-[^}]+\}')

if ($ComposeDefaults.Count -gt 0) {
    Write-Host "  Found default values in docker-compose.yml:" -ForegroundColor Yellow
    foreach ($default in $ComposeDefaults) {
        Write-Host "     $($default.Value)"
    }
    Write-Host "     Note: Defaults should be in .env file, not docker-compose.yml"
    $Warnings++
} else {
    Write-Host "  No conflicting default values found" -ForegroundColor Green
}
Write-Host ""

# ============================================================================
# Check 6: Environment Variable Documentation
# ============================================================================
Write-Host "Checking environment variable documentation..." -ForegroundColor Yellow
Write-Host ""

$envContent = Get-Content $EnvExample
$Undocumented = 0

for ($i = 0; $i -lt $envContent.Count; $i++) {
    $line = $envContent[$i]
    
    if ($line -match '^[A-Z_][A-Z0-9_]+=') {
        $varName = ($line -split '=')[0]
        
        # Check if there's a comment in previous 3 lines
        $hasComment = $false
        for ($j = 1; $j -le 3; $j++) {
            $prevIndex = $i - $j
            if ($prevIndex -ge 0) {
                $prevLine = $envContent[$prevIndex]
                if ($prevLine -match '^#' -and $prevLine -notmatch '^#\s*-+') {
                    $hasComment = $true
                    break
                }
            }
        }
        
        if (-not $hasComment) {
            Write-Host "  $varName has no documentation comment" -ForegroundColor Yellow
            $Undocumented++
            $Warnings++
        }
    }
}

if ($Undocumented -eq 0) {
    Write-Host "  All variables are documented" -ForegroundColor Green
} else {
    Write-Host "  Found $Undocumented undocumented variables" -ForegroundColor Yellow
}
Write-Host ""

# ============================================================================
# Summary
# ============================================================================
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Configuration Consistency Check Summary" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Variables found:"
Write-Host "  - docker-compose.yml: $($ComposeVars.Count)"
Write-Host "  - Backend Settings:   $($BackendVars.Count)"
Write-Host "  - Frontend env:       $($FrontendVars.Count)"
Write-Host "  - .env.example:       $($ExampleVars.Count)"
Write-Host ""

if ($Errors -eq 0 -and $Warnings -eq 0) {
    Write-Host "All configuration consistency checks passed!" -ForegroundColor Green
    Write-Host ""
    exit 0
} elseif ($Errors -eq 0) {
    Write-Host "Configuration consistency check completed with $Warnings warning(s)" -ForegroundColor Yellow
    Write-Host ""
    exit 0
} else {
    Write-Host "Configuration consistency check failed with $Errors error(s) and $Warnings warning(s)" -ForegroundColor Red
    Write-Host ""
    exit 1
}
