#!/bin/bash
# ============================================================================
# Co-Op OS v1.0.3 Documentation Validation Script
# ============================================================================
# This script validates documentation files for:
# - File references exist
# - Commands are valid
# - Environment variables are documented
# - No broken links
#
# Usage:
#   bash scripts/check-docs.sh
# ============================================================================

set -e

echo "Co-Op OS v1.0.3 - Documentation Validation"
echo "==========================================="
echo ""

ERRORS=0
WARNINGS=0

# ============================================================================
# Check 1: File References in Documentation
# ============================================================================
echo "📁 Checking file references in documentation..."
echo ""

# Find all markdown files
MARKDOWN_FILES=$(find docs .kiro/steering .kiro/specs -name "*.md" 2>/dev/null || true)

for doc in $MARKDOWN_FILES; do
    # Extract file paths (looking for patterns like services/*, apps/*, etc.)
    # Match patterns like: services/api/app/config.py, apps/web/src/lib/api.ts
    grep -oE '(services|apps|infrastructure|cli|docs|\.kiro)/[a-zA-Z0-9_/.-]+\.(py|ts|tsx|js|jsx|yml|yaml|json|toml|md|sh|ps1)' "$doc" 2>/dev/null | while read -r ref; do
        # Skip URLs and example paths
        if [[ "$ref" =~ ^http ]] || [[ "$ref" =~ example ]] || [[ "$ref" =~ \{.*\} ]]; then
            continue
        fi
        
        if [ ! -f "$ref" ] && [ ! -d "$ref" ]; then
            echo "  ❌ $doc references non-existent: $ref"
            ERRORS=$((ERRORS + 1))
        fi
    done
done

if [ $ERRORS -eq 0 ]; then
    echo "  ✅ All file references are valid"
fi
echo ""

# ============================================================================
# Check 2: Environment Variables in Documentation
# ============================================================================
echo "🔐 Checking environment variables in documentation..."
echo ""

# Extract env vars from documentation (looking for ${VAR} or $VAR patterns)
DOC_ENV_VARS=$(grep -hoE '\$\{?[A-Z_][A-Z0-9_]+\}?' $MARKDOWN_FILES 2>/dev/null | sed 's/[${}]//g' | sort -u || true)

# Check if .env.example exists
if [ -f "infrastructure/docker/.env.example" ]; then
    for var in $DOC_ENV_VARS; do
        # Skip common shell variables
        if [[ "$var" =~ ^(PATH|HOME|USER|PWD|SHELL)$ ]]; then
            continue
        fi
        
        if ! grep -q "^${var}=" infrastructure/docker/.env.example 2>/dev/null; then
            echo "  ⚠️  $var referenced in docs but not in .env.example"
            WARNINGS=$((WARNINGS + 1))
        fi
    done
    
    if [ $WARNINGS -eq 0 ]; then
        echo "  ✅ All environment variables are documented"
    fi
else
    echo "  ⚠️  infrastructure/docker/.env.example not found"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# ============================================================================
# Check 3: Command Syntax in Documentation
# ============================================================================
echo "⚙️  Checking command syntax in documentation..."
echo ""

# Check for localhost references that should use service names in Docker context
LOCALHOST_REFS=$(grep -rn "localhost:5432\|localhost:6379\|localhost:9000" docs/ .kiro/ 2>/dev/null | grep -v ".env.example" | grep -v "NEXT_PUBLIC" || true)

if [ -n "$LOCALHOST_REFS" ]; then
    echo "  ⚠️  Found localhost references in documentation:"
    echo "$LOCALHOST_REFS" | while read -r line; do
        echo "     $line"
    done
    echo "     Note: Use service names (postgres:5432, redis:6379, minio:9000) for Docker internal"
    WARNINGS=$((WARNINGS + 1))
else
    echo "  ✅ No problematic localhost references found"
fi
echo ""

# ============================================================================
# Check 4: Outdated File References
# ============================================================================
echo "📝 Checking for outdated file references..."
echo ""

OUTDATED_REFS=(
    "docs/CO_OP_SOLO_DEVELOPER_ARCHITECTURE.md"
    "docs/CO_OP_SOLO_TASKS_UPDATED.md"
    "docs/stage1_implementation.md"
    "docs/stage2_implementation.md"
    "docs/stage3_implementation.md"
    "docs/stage4_implementation.md"
    "phase-0-production-ready"
)

FOUND_OUTDATED=0
for ref in "${OUTDATED_REFS[@]}"; do
    if grep -r "$ref" docs/ .kiro/steering/ .kiro/specs/production-readiness-v1/ 2>/dev/null | grep -v "archive" | grep -v "\.git" >/dev/null; then
        echo "  ⚠️  Found reference to outdated file: $ref"
        echo "     Should use docs/stages/phase-X/ or docs/archive/ instead"
        FOUND_OUTDATED=1
        WARNINGS=$((WARNINGS + 1))
    fi
done

if [ $FOUND_OUTDATED -eq 0 ]; then
    echo "  ✅ No outdated file references found"
fi
echo ""

# ============================================================================
# Check 5: Broken Internal Links
# ============================================================================
echo "🔗 Checking for broken internal links..."
echo ""

# Extract markdown links [text](path)
BROKEN_LINKS=0
for doc in $MARKDOWN_FILES; do
    # Extract relative links (not URLs)
    grep -oE '\[([^\]]+)\]\(([^)]+)\)' "$doc" 2>/dev/null | grep -oE '\(([^)]+)\)' | sed 's/[()]//g' | while read -r link; do
        # Skip URLs, anchors, and mailto links
        if [[ "$link" =~ ^http ]] || [[ "$link" =~ ^# ]] || [[ "$link" =~ ^mailto ]]; then
            continue
        fi
        
        # Remove anchor from link
        link_path="${link%%#*}"
        
        # Resolve relative path
        doc_dir=$(dirname "$doc")
        full_path="$doc_dir/$link_path"
        
        # Normalize path
        full_path=$(realpath -m "$full_path" 2>/dev/null || echo "$full_path")
        
        if [ ! -f "$full_path" ] && [ ! -d "$full_path" ]; then
            echo "  ❌ $doc has broken link: $link"
            BROKEN_LINKS=$((BROKEN_LINKS + 1))
            ERRORS=$((ERRORS + 1))
        fi
    done
done

if [ $BROKEN_LINKS -eq 0 ]; then
    echo "  ✅ No broken internal links found"
fi
echo ""

# ============================================================================
# Check 6: Required Documentation Files
# ============================================================================
echo "📋 Checking for required documentation files..."
echo ""

REQUIRED_DOCS=(
    "docs/PROJECT_STRUCTURE.md"
    "docs/INSTALLATION.md"
    "docs/CI_CD_SETUP.md"
    "docs/ENV_VARIABLES_REFERENCE.md"
    ".kiro/steering/architecture.md"
    ".kiro/steering/project.md"
    ".kiro/steering/constraints.md"
)

MISSING_DOCS=0
for doc in "${REQUIRED_DOCS[@]}"; do
    if [ ! -f "$doc" ]; then
        echo "  ❌ Missing required documentation: $doc"
        MISSING_DOCS=$((MISSING_DOCS + 1))
        ERRORS=$((ERRORS + 1))
    fi
done

if [ $MISSING_DOCS -eq 0 ]; then
    echo "  ✅ All required documentation files exist"
fi
echo ""

# ============================================================================
# Summary
# ============================================================================
echo "=========================================="
echo "Documentation Validation Summary"
echo "=========================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ All documentation validation checks passed!"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  Documentation validation completed with $WARNINGS warning(s)"
    echo ""
    exit 0
else
    echo "❌ Documentation validation failed with $ERRORS error(s) and $WARNINGS warning(s)"
    echo ""
    exit 1
fi
