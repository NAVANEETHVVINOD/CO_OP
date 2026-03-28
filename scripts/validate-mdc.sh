#!/bin/bash
# Validation script for MDC files
# Checks file references, commands, and environment variables

set -e

echo "🔍 Validating MDC files..."
echo ""

ERRORS=0

# Check file references in MDC files
echo "📁 Checking file references..."
while IFS= read -r file; do
    # Extract file paths from MDC files (looking for patterns like docs/*, services/*, apps/*)
    grep -oE '(docs|services|apps|infrastructure|cli)/[a-zA-Z0-9_/.-]+\.(md|py|ts|tsx|yml|yaml|json|toml)' "$file" 2>/dev/null | while read -r ref; do
        if [ ! -f "$ref" ] && [ ! -d "$ref" ]; then
            echo "❌ $file references non-existent path: $ref"
            ERRORS=$((ERRORS + 1))
        fi
    done
done < <(find docs/rules -name "*.mdc")

# Check environment variables in MDC files match .env.example
echo ""
echo "🔐 Checking environment variables..."

# Extract env vars from MDC files
MDC_VARS=$(grep -hoE '\$\{[A-Z_]+\}' docs/rules/*.mdc | sort -u | sed 's/[${}]//g')

# Check if .env.example exists
if [ -f "infrastructure/docker/.env.example" ]; then
    for var in $MDC_VARS; do
        if ! grep -q "^${var}=" infrastructure/docker/.env.example; then
            echo "⚠️  Environment variable $var referenced in MDC but not in .env.example"
            ERRORS=$((ERRORS + 1))
        fi
    done
else
    echo "⚠️  infrastructure/docker/.env.example not found"
    ERRORS=$((ERRORS + 1))
fi

# Check for common command patterns
echo ""
echo "⚙️  Checking command syntax..."

# Check for localhost references that should use service names
if grep -r "localhost:5432" docs/rules/*.mdc 2>/dev/null; then
    echo "⚠️  Found localhost:5432 in MDC files - should use postgres:5432 for Docker internal"
    ERRORS=$((ERRORS + 1))
fi

# Check for outdated file references
echo ""
echo "📝 Checking for outdated file references..."

OUTDATED_REFS=(
    "docs/CO_OP_SOLO_DEVELOPER_ARCHITECTURE.md"
    "docs/CO_OP_SOLO_TASKS_UPDATED.md"
    "docs/stage1_implementation.md"
    "docs/stage2_implementation.md"
    "docs/stage3_implementation.md"
    "docs/stage4_implementation.md"
)

for ref in "${OUTDATED_REFS[@]}"; do
    if grep -r "$ref" docs/rules/*.mdc 2>/dev/null; then
        echo "❌ Found outdated reference to $ref in MDC files"
        echo "   Should use docs/stages/phase-X/ or docs/archive/ instead"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✅ All MDC validation checks passed!"
    exit 0
else
    echo "❌ Found $ERRORS validation errors"
    exit 1
fi
