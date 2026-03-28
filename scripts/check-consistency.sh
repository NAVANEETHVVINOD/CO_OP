#!/bin/bash
# ============================================================================
# Co-Op OS v1.0.3 Configuration Consistency Check Script
# ============================================================================
# This script verifies configuration consistency across:
# - docker-compose.yml environment variables
# - Backend Settings class (services/api/app/config.py)
# - Frontend env module (apps/web/src/lib/env.ts)
# - .env.example files
#
# Usage:
#   bash scripts/check-consistency.sh
# ============================================================================

set -e

echo "Co-Op OS v1.0.3 - Configuration Consistency Check"
echo "=================================================="
echo ""

ERRORS=0
WARNINGS=0

# ============================================================================
# Extract Environment Variables from Different Sources
# ============================================================================

echo "🔍 Extracting environment variables from configuration files..."
echo ""

# Extract from docker-compose.yml
COMPOSE_FILE="infrastructure/docker/docker-compose.yml"
if [ -f "$COMPOSE_FILE" ]; then
    COMPOSE_VARS=$(grep -oE '\$\{[A-Z_][A-Z0-9_]+[:-]?' "$COMPOSE_FILE" | sed 's/[${}:-]//g' | sort -u)
    echo "  ✓ Found $(echo "$COMPOSE_VARS" | wc -w) variables in docker-compose.yml"
else
    echo "  ❌ docker-compose.yml not found at $COMPOSE_FILE"
    ERRORS=$((ERRORS + 1))
    exit 1
fi

# Extract from Backend Settings (config.py)
CONFIG_FILE="services/api/app/config.py"
if [ -f "$CONFIG_FILE" ]; then
    # Extract field names from Settings class (looking for: field_name: type)
    BACKEND_VARS=$(grep -oE '^\s+[A-Z_][A-Z0-9_]+:' "$CONFIG_FILE" | sed 's/[: ]//g' | sort -u)
    echo "  ✓ Found $(echo "$BACKEND_VARS" | wc -w) variables in Backend Settings"
else
    echo "  ❌ config.py not found at $CONFIG_FILE"
    ERRORS=$((ERRORS + 1))
fi

# Extract from Frontend env module (env.ts)
ENV_TS_FILE="apps/web/src/lib/env.ts"
if [ -f "$ENV_TS_FILE" ]; then
    # Extract NEXT_PUBLIC_ variables from process.env references
    FRONTEND_VARS=$(grep -oE 'process\.env\.[A-Z_][A-Z0-9_]+' "$ENV_TS_FILE" | sed 's/process\.env\.//g' | sort -u)
    echo "  ✓ Found $(echo "$FRONTEND_VARS" | wc -w) variables in Frontend env module"
else
    echo "  ⚠️  env.ts not found at $ENV_TS_FILE (may not be created yet)"
    FRONTEND_VARS=""
    WARNINGS=$((WARNINGS + 1))
fi

# Extract from .env.example
ENV_EXAMPLE="infrastructure/docker/.env.example"
if [ -f "$ENV_EXAMPLE" ]; then
    EXAMPLE_VARS=$(grep -oE '^[A-Z_][A-Z0-9_]+=' "$ENV_EXAMPLE" | sed 's/=//g' | sort -u)
    echo "  ✓ Found $(echo "$EXAMPLE_VARS" | wc -w) variables in .env.example"
else
    echo "  ❌ .env.example not found at $ENV_EXAMPLE"
    ERRORS=$((ERRORS + 1))
    exit 1
fi

echo ""

# ============================================================================
# Check 1: Docker Compose Variables in .env.example
# ============================================================================
echo "📋 Checking docker-compose.yml variables are in .env.example..."
echo ""

MISSING_IN_EXAMPLE=0
for var in $COMPOSE_VARS; do
    if ! echo "$EXAMPLE_VARS" | grep -q "^${var}$"; then
        echo "  ❌ $var used in docker-compose.yml but not in .env.example"
        MISSING_IN_EXAMPLE=$((MISSING_IN_EXAMPLE + 1))
        ERRORS=$((ERRORS + 1))
    fi
done

if [ $MISSING_IN_EXAMPLE -eq 0 ]; then
    echo "  ✅ All docker-compose.yml variables are in .env.example"
fi
echo ""

# ============================================================================
# Check 2: Backend Settings Variables in .env.example
# ============================================================================
echo "🔧 Checking Backend Settings variables are in .env.example..."
echo ""

MISSING_BACKEND=0
for var in $BACKEND_VARS; do
    # Skip internal fields that aren't environment variables
    if [[ "$var" =~ ^(model_config|VERSION)$ ]]; then
        continue
    fi
    
    if ! echo "$EXAMPLE_VARS" | grep -q "^${var}$"; then
        echo "  ❌ $var in Backend Settings but not in .env.example"
        MISSING_BACKEND=$((MISSING_BACKEND + 1))
        ERRORS=$((ERRORS + 1))
    fi
done

if [ $MISSING_BACKEND -eq 0 ]; then
    echo "  ✅ All Backend Settings variables are in .env.example"
fi
echo ""

# ============================================================================
# Check 3: Frontend Variables in .env.example
# ============================================================================
if [ -n "$FRONTEND_VARS" ]; then
    echo "🎨 Checking Frontend env variables are in .env.example..."
    echo ""
    
    MISSING_FRONTEND=0
    for var in $FRONTEND_VARS; do
        if ! echo "$EXAMPLE_VARS" | grep -q "^${var}$"; then
            echo "  ❌ $var in Frontend env module but not in .env.example"
            MISSING_FRONTEND=$((MISSING_FRONTEND + 1))
            ERRORS=$((ERRORS + 1))
        fi
    done
    
    if [ $MISSING_FRONTEND -eq 0 ]; then
        echo "  ✅ All Frontend env variables are in .env.example"
    fi
    echo ""
fi

# ============================================================================
# Check 4: Naming Convention Consistency
# ============================================================================
echo "📝 Checking naming convention consistency..."
echo ""

# Check for inconsistent naming (e.g., MINIO_URL vs MINIO_ENDPOINT)
NAMING_ISSUES=0

# Common patterns to check
declare -A RELATED_VARS=(
    ["MINIO"]="MINIO_URL MINIO_ENDPOINT MINIO_ROOT_USER MINIO_ROOT_PASSWORD"
    ["DATABASE"]="DATABASE_URL DB_PASS"
    ["REDIS"]="REDIS_URL"
    ["OLLAMA"]="OLLAMA_URL"
    ["API"]="API_BASE_URL NEXT_PUBLIC_API_URL"
    ["FRONTEND"]="FRONTEND_URL"
)

for prefix in "${!RELATED_VARS[@]}"; do
    vars="${RELATED_VARS[$prefix]}"
    for var in $vars; do
        # Check if variable exists in any source
        in_compose=$(echo "$COMPOSE_VARS" | grep -c "^${var}$" || true)
        in_backend=$(echo "$BACKEND_VARS" | grep -c "^${var}$" || true)
        in_example=$(echo "$EXAMPLE_VARS" | grep -c "^${var}$" || true)
        
        # If variable is used, it should be in .env.example
        if [ $in_compose -gt 0 ] || [ $in_backend -gt 0 ]; then
            if [ $in_example -eq 0 ]; then
                echo "  ⚠️  $var is used but not in .env.example"
                NAMING_ISSUES=$((NAMING_ISSUES + 1))
                WARNINGS=$((WARNINGS + 1))
            fi
        fi
    done
done

if [ $NAMING_ISSUES -eq 0 ]; then
    echo "  ✅ Naming conventions are consistent"
fi
echo ""

# ============================================================================
# Check 5: Required Variables for Production
# ============================================================================
echo "🔒 Checking required variables for production..."
echo ""

REQUIRED_PROD_VARS=(
    "DB_PASS"
    "SECRET_KEY"
    "MINIO_ROOT_USER"
    "MINIO_ROOT_PASSWORD"
    "OLLAMA_URL"
    "API_BASE_URL"
    "FRONTEND_URL"
    "NEXT_PUBLIC_API_URL"
)

MISSING_REQUIRED=0
for var in "${REQUIRED_PROD_VARS[@]}"; do
    if ! echo "$EXAMPLE_VARS" | grep -q "^${var}$"; then
        echo "  ❌ Required production variable $var not in .env.example"
        MISSING_REQUIRED=$((MISSING_REQUIRED + 1))
        ERRORS=$((ERRORS + 1))
    fi
done

if [ $MISSING_REQUIRED -eq 0 ]; then
    echo "  ✅ All required production variables are documented"
fi
echo ""

# ============================================================================
# Check 6: Conflicting Default Values
# ============================================================================
echo "⚖️  Checking for conflicting default values..."
echo ""

# Check if docker-compose.yml has hardcoded defaults that conflict with .env.example
CONFLICTING_DEFAULTS=0

# Look for patterns like ${VAR:-default_value}
COMPOSE_DEFAULTS=$(grep -oE '\$\{[A-Z_][A-Z0-9_]+:-[^}]+\}' "$COMPOSE_FILE" 2>/dev/null || true)

if [ -n "$COMPOSE_DEFAULTS" ]; then
    echo "  ⚠️  Found default values in docker-compose.yml:"
    echo "$COMPOSE_DEFAULTS" | while read -r default; do
        echo "     $default"
    done
    echo "     Note: Defaults should be in .env file, not docker-compose.yml"
    CONFLICTING_DEFAULTS=$((CONFLICTING_DEFAULTS + 1))
    WARNINGS=$((WARNINGS + 1))
fi

if [ $CONFLICTING_DEFAULTS -eq 0 ]; then
    echo "  ✅ No conflicting default values found"
fi
echo ""

# ============================================================================
# Check 7: Environment Variable Documentation
# ============================================================================
echo "📚 Checking environment variable documentation..."
echo ""

# Check if .env.example has comments for each variable
UNDOCUMENTED=0
while IFS= read -r line; do
    # Check if this is a variable definition
    if [[ "$line" =~ ^[A-Z_][A-Z0-9_]+=.* ]]; then
        var_name=$(echo "$line" | cut -d'=' -f1)
        
        # Check if there's a comment above this variable (within 3 lines)
        line_num=$(grep -n "^${var_name}=" "$ENV_EXAMPLE" | cut -d':' -f1)
        
        # Look for comment in previous 3 lines
        has_comment=0
        for i in 1 2 3; do
            prev_line=$((line_num - i))
            if [ $prev_line -gt 0 ]; then
                prev_content=$(sed -n "${prev_line}p" "$ENV_EXAMPLE")
                if [[ "$prev_content" =~ ^# ]] && [[ ! "$prev_content" =~ ^#[[:space:]]*-+ ]]; then
                    has_comment=1
                    break
                fi
            fi
        done
        
        if [ $has_comment -eq 0 ]; then
            echo "  ⚠️  $var_name has no documentation comment"
            UNDOCUMENTED=$((UNDOCUMENTED + 1))
            WARNINGS=$((WARNINGS + 1))
        fi
    fi
done < "$ENV_EXAMPLE"

if [ $UNDOCUMENTED -eq 0 ]; then
    echo "  ✅ All variables are documented"
else
    echo "  ⚠️  Found $UNDOCUMENTED undocumented variables"
fi
echo ""

# ============================================================================
# Summary
# ============================================================================
echo "=================================================="
echo "Configuration Consistency Check Summary"
echo "=================================================="
echo ""
echo "Variables found:"
echo "  - docker-compose.yml: $(echo "$COMPOSE_VARS" | wc -w)"
echo "  - Backend Settings:   $(echo "$BACKEND_VARS" | wc -w)"
echo "  - Frontend env:       $(echo "$FRONTEND_VARS" | wc -w)"
echo "  - .env.example:       $(echo "$EXAMPLE_VARS" | wc -w)"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ All configuration consistency checks passed!"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  Configuration consistency check completed with $WARNINGS warning(s)"
    echo ""
    exit 0
else
    echo "❌ Configuration consistency check failed with $ERRORS error(s) and $WARNINGS warning(s)"
    echo ""
    exit 1
fi
