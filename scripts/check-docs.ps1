# ============================================================================
# Co-Op OS v1.0.3 Documentation Validation Script (PowerShell)
# ============================================================================

param([switch]$Verbose)

Write-Host "Co-Op OS v1.0.3 - Documentation Validation" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

$Errors = 0
$Warnings = 0

# ============================================================================
# Check 1: File References in Documentation
# ============================================================================
Write-Host "Checking file references in documentation..." -ForegroundColor Yellow
Write-Host ""

$MarkdownFiles = @()
$MarkdownFiles += Get-ChildItem -Path "docs" -Filter "*.md" -Recurse -ErrorAction SilentlyContinue
$MarkdownFiles += Get-ChildItem -Path ".kiro/steering" -Filter "*.md" -Recurse -ErrorAction SilentlyContinue
$MarkdownFiles += Get-ChildItem -Path ".kiro/specs" -Filter "*.md" -Recurse -ErrorAction SilentlyContinue

foreach ($doc in $MarkdownFiles) {
    $content = Get-Content $doc.FullName -Raw
    
    # Extract file paths
    $matches = [regex]::Matches($content, '(services|apps|infrastructure|cli|docs|\.kiro)/[a-zA-Z0-9_/.-]+\.(py|ts|tsx|js|jsx|yml|yaml|json|toml|md|sh|ps1)')
    
    foreach ($match in $matches) {
        $ref = $match.Value
        
        # Skip URLs and example paths
        if ($ref -match '^http' -or $ref -match 'example' -or $ref -match '\{.*\}') {
            continue
        }
        
        if (-not (Test-Path $ref)) {
            Write-Host "  $($doc.Name) references non-existent: $ref" -ForegroundColor Red
            $Errors++
        }
    }
}

if ($Errors -eq 0) {
    Write-Host "  All file references are valid" -ForegroundColor Green
}
Write-Host ""

# ============================================================================
# Check 2: Environment Variables in Documentation
# ============================================================================
Write-Host "Checking environment variables in documentation..." -ForegroundColor Yellow
Write-Host ""

$DocEnvVars = @()
foreach ($doc in $MarkdownFiles) {
    $content = Get-Content $doc.FullName -Raw
    $matches = [regex]::Matches($content, '\$\{?[A-Z_][A-Z0-9_]+\}?')
    
    foreach ($match in $matches) {
        $var = $match.Value -replace '[${}]', ''
        if ($var -notmatch '^(PATH|HOME|USER|PWD|SHELL)$') {
            $DocEnvVars += $var
        }
    }
}

$DocEnvVars = $DocEnvVars | Select-Object -Unique

if (Test-Path "infrastructure/docker/.env.example") {
    $EnvExample = Get-Content "infrastructure/docker/.env.example"
    
    foreach ($var in $DocEnvVars) {
        if ($EnvExample -notmatch "^${var}=") {
            Write-Host "  $var referenced in docs but not in .env.example" -ForegroundColor Yellow
            $Warnings++
        }
    }
    
    if ($Warnings -eq 0) {
        Write-Host "  All environment variables are documented" -ForegroundColor Green
    }
} else {
    Write-Host "  infrastructure/docker/.env.example not found" -ForegroundColor Yellow
    $Warnings++
}
Write-Host ""

# ============================================================================
# Check 3: Command Syntax in Documentation
# ============================================================================
Write-Host "Checking command syntax in documentation..." -ForegroundColor Yellow
Write-Host ""

$LocalhostRefs = @()
foreach ($doc in $MarkdownFiles) {
    $content = Get-Content $doc.FullName -Raw
    
    if ($content -match 'localhost:5432|localhost:6379|localhost:9000' -and 
        $doc.Name -notmatch '.env.example' -and 
        $content -notmatch 'NEXT_PUBLIC') {
        $LocalhostRefs += $doc.Name
    }
}

if ($LocalhostRefs.Count -gt 0) {
    Write-Host "  Found localhost references in documentation:" -ForegroundColor Yellow
    foreach ($ref in $LocalhostRefs) {
        Write-Host "     $ref"
    }
    Write-Host "     Note: Use service names (postgres:5432, redis:6379, minio:9000) for Docker internal"
    $Warnings++
} else {
    Write-Host "  No problematic localhost references found" -ForegroundColor Green
}
Write-Host ""

# ============================================================================
# Check 4: Outdated File References
# ============================================================================
Write-Host "Checking for outdated file references..." -ForegroundColor Yellow
Write-Host ""

$OutdatedRefs = @(
    "docs/CO_OP_SOLO_DEVELOPER_ARCHITECTURE.md",
    "docs/CO_OP_SOLO_TASKS_UPDATED.md",
    "docs/stage1_implementation.md",
    "docs/stage2_implementation.md",
    "docs/stage3_implementation.md",
    "docs/stage4_implementation.md",
    "phase-0-production-ready"
)

$FoundOutdated = $false
foreach ($ref in $OutdatedRefs) {
    foreach ($doc in $MarkdownFiles) {
        if ($doc.FullName -notmatch 'archive' -and $doc.FullName -notmatch '\.git') {
            $content = Get-Content $doc.FullName -Raw
            if ($content -match [regex]::Escape($ref)) {
                Write-Host "  Found reference to outdated file: $ref in $($doc.Name)" -ForegroundColor Yellow
                Write-Host "     Should use docs/stages/phase-X/ or docs/archive/ instead"
                $FoundOutdated = $true
                $Warnings++
            }
        }
    }
}

if (-not $FoundOutdated) {
    Write-Host "  No outdated file references found" -ForegroundColor Green
}
Write-Host ""

# ============================================================================
# Check 5: Required Documentation Files
# ============================================================================
Write-Host "Checking for required documentation files..." -ForegroundColor Yellow
Write-Host ""

$RequiredDocs = @(
    "docs/PROJECT_STRUCTURE.md",
    "docs/INSTALLATION.md",
    "docs/CI_CD_SETUP.md",
    "docs/ENV_VARIABLES_REFERENCE.md",
    ".kiro/steering/architecture.md",
    ".kiro/steering/project.md",
    ".kiro/steering/constraints.md"
)

$MissingDocs = 0
foreach ($doc in $RequiredDocs) {
    if (-not (Test-Path $doc)) {
        Write-Host "  Missing required documentation: $doc" -ForegroundColor Red
        $MissingDocs++
        $Errors++
    }
}

if ($MissingDocs -eq 0) {
    Write-Host "  All required documentation files exist" -ForegroundColor Green
}
Write-Host ""

# ============================================================================
# Summary
# ============================================================================
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Documentation Validation Summary" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

if ($Errors -eq 0 -and $Warnings -eq 0) {
    Write-Host "All documentation validation checks passed!" -ForegroundColor Green
    Write-Host ""
    exit 0
} elseif ($Errors -eq 0) {
    Write-Host "Documentation validation completed with $Warnings warning(s)" -ForegroundColor Yellow
    Write-Host ""
    exit 0
} else {
    Write-Host "Documentation validation failed with $Errors error(s) and $Warnings warning(s)" -ForegroundColor Red
    Write-Host ""
    exit 1
}
