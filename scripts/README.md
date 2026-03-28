# Co-Op OS Validation Scripts

This directory contains validation scripts for ensuring production readiness of the Co-Op OS v1.0.3 system.

## Available Scripts

### 1. Environment Validation (`validate-env.sh` / `validate-env.ps1`)

**Location:** `infrastructure/docker/validate-env.sh` (Bash) or `infrastructure/docker/validate-env.ps1` (PowerShell)

**Purpose:** Validates that all required environment variables are set in the `.env` file before starting Docker services.

**Usage:**

```bash
# Bash (Linux/Mac)
bash infrastructure/docker/validate-env.sh [path-to-env-file]

# PowerShell (Windows)
powershell -File infrastructure/docker/validate-env.ps1 [path-to-env-file]
```

**What it checks:**
- `.env` file exists
- All required environment variables are set
- `SECRET_KEY` is at least 32 characters long
- `ENVIRONMENT` value is valid (development/staging/production)

**Example output:**
```
✅ All required environment variables are set

Configuration summary:
  Environment:     development
  Database:        postgresql+asyncpg://coop:***
  Redis:           redis://redis:6379/0
  MinIO:           minio:9000
  API URL:         http://co-op-api:8000
  Frontend URL:    http://co-op-web:3000
  Public API URL:  http://localhost:8000

✓ Ready to start Docker services
```

### 2. Documentation Validation (`check-docs.sh` / `check-docs.ps1`)

**Location:** `scripts/check-docs.sh` (Bash) or `scripts/check-docs.ps1` (PowerShell)

**Purpose:** Validates documentation files for correctness and consistency.

**Usage:**

```bash
# Bash (Linux/Mac)
bash scripts/check-docs.sh

# PowerShell (Windows)
powershell -File scripts/check-docs.ps1
```

**What it checks:**
- File references in documentation exist
- Environment variables in documentation are in `.env.example`
- Command syntax is correct (no problematic localhost references)
- No outdated file references
- No broken internal links
- All required documentation files exist

**Checks performed:**
1. **File References** - Verifies all file paths mentioned in docs exist
2. **Environment Variables** - Ensures all env vars in docs are documented in `.env.example`
3. **Command Syntax** - Checks for localhost references that should use service names
4. **Outdated References** - Detects references to archived or deprecated files
5. **Broken Links** - Validates internal markdown links
6. **Required Files** - Ensures critical documentation files exist

### 3. Configuration Consistency Check (`check-consistency.sh` / `check-consistency.ps1`)

**Location:** `scripts/check-consistency.sh` (Bash) or `scripts/check-consistency.ps1` (PowerShell)

**Purpose:** Verifies configuration consistency across all system components.

**Usage:**

```bash
# Bash (Linux/Mac)
bash scripts/check-consistency.sh

# PowerShell (Windows)
powershell -File scripts/check-consistency.ps1
```

**What it checks:**
- Environment variables in `docker-compose.yml` are in `.env.example`
- Backend Settings class variables are in `.env.example`
- Frontend env module variables are in `.env.example`
- Naming convention consistency across components
- Required production variables are documented
- No conflicting default values
- All variables have documentation comments

**Example output:**
```
==================================================
Configuration Consistency Check Summary
==================================================

Variables found:
  - docker-compose.yml: 25
  - Backend Settings:   21
  - Frontend env:       4
  - .env.example:       26

✅ All configuration consistency checks passed!
```

### 4. MDC File Validation (`validate-mdc.sh`)

**Location:** `scripts/validate-mdc.sh`

**Purpose:** Validates MDC (Markdown Context) files in `docs/rules/` for correctness.

**Usage:**

```bash
bash scripts/validate-mdc.sh
```

**What it checks:**
- File references in MDC files exist
- Environment variables in MDC files are in `.env.example`
- No localhost references that should use service names
- No outdated file references

## Running All Validation Scripts

To run all validation scripts at once:

### Bash (Linux/Mac)

```bash
#!/bin/bash
echo "Running all validation scripts..."
echo ""

echo "1. Environment Validation"
bash infrastructure/docker/validate-env.sh
echo ""

echo "2. Documentation Validation"
bash scripts/check-docs.sh
echo ""

echo "3. Configuration Consistency Check"
bash scripts/check-consistency.sh
echo ""

echo "4. MDC File Validation"
bash scripts/validate-mdc.sh
echo ""

echo "✅ All validation scripts completed!"
```

### PowerShell (Windows)

```powershell
Write-Host "Running all validation scripts..." -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Environment Validation" -ForegroundColor Yellow
powershell -File infrastructure/docker/validate-env.ps1
Write-Host ""

Write-Host "2. Documentation Validation" -ForegroundColor Yellow
powershell -File scripts/check-docs.ps1
Write-Host ""

Write-Host "3. Configuration Consistency Check" -ForegroundColor Yellow
powershell -File scripts/check-consistency.ps1
Write-Host ""

Write-Host "All validation scripts completed!" -ForegroundColor Green
```

## Integration with CI/CD

These scripts can be integrated into CI/CD pipelines to ensure production readiness:

```yaml
# Example GitHub Actions workflow
name: Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Validate Environment Configuration
        run: bash infrastructure/docker/validate-env.sh infrastructure/docker/.env.example
      
      - name: Validate Documentation
        run: bash scripts/check-docs.sh
      
      - name: Check Configuration Consistency
        run: bash scripts/check-consistency.sh
      
      - name: Validate MDC Files
        run: bash scripts/validate-mdc.sh
```

## Exit Codes

All scripts follow standard exit code conventions:

- `0` - All checks passed (or passed with warnings only)
- `1` - One or more checks failed

## Troubleshooting

### Script Permission Denied (Linux/Mac)

If you get a "permission denied" error, make the script executable:

```bash
chmod +x scripts/check-docs.sh
chmod +x scripts/check-consistency.sh
chmod +x scripts/validate-mdc.sh
chmod +x infrastructure/docker/validate-env.sh
```

### PowerShell Execution Policy (Windows)

If PowerShell blocks script execution, you may need to adjust the execution policy:

```powershell
# For current session only
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Or run with bypass flag
powershell -ExecutionPolicy Bypass -File scripts/check-docs.ps1
```

## Contributing

When adding new validation scripts:

1. Create both Bash (`.sh`) and PowerShell (`.ps1`) versions
2. Follow the existing script structure and output format
3. Use clear error messages with actionable guidance
4. Document the script in this README
5. Add the script to the "Running All Validation Scripts" section

## Related Documentation

- [Environment Variables Reference](../docs/ENV_VARIABLES_REFERENCE.md)
- [Project Structure](../docs/PROJECT_STRUCTURE.md)
- [CI/CD Setup](../docs/CI_CD_SETUP.md)
- [Installation Guide](../docs/INSTALLATION.md)
