# ============================================================================
# Co-Op OS v1.0.3 - Run All Validation Scripts (PowerShell)
# ============================================================================

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Co-Op OS v1.0.3 - Complete Validation Suite                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$TotalErrors = 0
$TotalWarnings = 0

# ============================================================================
# 1. Environment Validation
# ============================================================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "1/4 Environment Validation" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""

$envScript = Join-Path $ProjectRoot "infrastructure\docker\validate-env.ps1"
$result = & powershell -File $envScript
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Host "Environment validation passed" -ForegroundColor Green
} else {
    Write-Host "Environment validation failed" -ForegroundColor Red
    $TotalErrors++
}
Write-Host ""

# ============================================================================
# 2. Documentation Validation
# ============================================================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "2/4 Documentation Validation" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""

$docsScript = Join-Path $ScriptDir "check-docs.ps1"
$result = & powershell -File $docsScript
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Host "Documentation validation passed" -ForegroundColor Green
} else {
    Write-Host "Documentation validation completed with warnings" -ForegroundColor Yellow
    $TotalWarnings++
}
Write-Host ""

# ============================================================================
# 3. Configuration Consistency Check
# ============================================================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "3/4 Configuration Consistency Check" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""

$consistencyScript = Join-Path $ScriptDir "check-consistency.ps1"
$result = & powershell -File $consistencyScript
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Host "Configuration consistency check passed" -ForegroundColor Green
} else {
    Write-Host "Configuration consistency check completed with warnings" -ForegroundColor Yellow
    $TotalWarnings++
}
Write-Host ""

# ============================================================================
# 4. MDC File Validation
# ============================================================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "4/4 MDC File Validation" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""

$mdcScript = Join-Path $ScriptDir "validate-mdc.sh"
if (Test-Path $mdcScript) {
    # Try to run with bash if available
    $bashPath = Get-Command bash -ErrorAction SilentlyContinue
    if ($bashPath) {
        $result = & bash $mdcScript
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -eq 0) {
            Write-Host "MDC file validation passed" -ForegroundColor Green
        } else {
            Write-Host "MDC file validation completed with warnings" -ForegroundColor Yellow
            $TotalWarnings++
        }
    } else {
        Write-Host "Bash not available, skipping MDC validation" -ForegroundColor Yellow
        $TotalWarnings++
    }
} else {
    Write-Host "MDC validation script not found, skipping" -ForegroundColor Yellow
    $TotalWarnings++
}
Write-Host ""

# ============================================================================
# Summary
# ============================================================================
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Validation Suite Summary                                      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

if ($TotalErrors -eq 0 -and $TotalWarnings -eq 0) {
    Write-Host "All validation checks passed!" -ForegroundColor Green
    Write-Host ""
    exit 0
} elseif ($TotalErrors -eq 0) {
    Write-Host "Validation completed with $TotalWarnings warning(s)" -ForegroundColor Yellow
    Write-Host ""
    exit 0
} else {
    Write-Host "Validation failed with $TotalErrors error(s) and $TotalWarnings warning(s)" -ForegroundColor Red
    Write-Host ""
    exit 1
}
