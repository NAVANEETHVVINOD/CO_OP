#!/bin/bash
# ============================================================================
# Co-Op OS v1.0.3 - Run All Validation Scripts
# ============================================================================
# This script runs all validation scripts in sequence
#
# Usage:
#   bash scripts/validate-all.sh
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Co-Op OS v1.0.3 - Complete Validation Suite                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

TOTAL_ERRORS=0
TOTAL_WARNINGS=0

# ============================================================================
# 1. Environment Validation
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1/4 Environment Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if bash "$PROJECT_ROOT/infrastructure/docker/validate-env.sh"; then
    echo "✅ Environment validation passed"
else
    echo "❌ Environment validation failed"
    TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
fi
echo ""

# ============================================================================
# 2. Documentation Validation
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2/4 Documentation Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if bash "$SCRIPT_DIR/check-docs.sh"; then
    echo "✅ Documentation validation passed"
else
    echo "⚠️  Documentation validation completed with warnings"
    TOTAL_WARNINGS=$((TOTAL_WARNINGS + 1))
fi
echo ""

# ============================================================================
# 3. Configuration Consistency Check
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3/4 Configuration Consistency Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if bash "$SCRIPT_DIR/check-consistency.sh"; then
    echo "✅ Configuration consistency check passed"
else
    echo "⚠️  Configuration consistency check completed with warnings"
    TOTAL_WARNINGS=$((TOTAL_WARNINGS + 1))
fi
echo ""

# ============================================================================
# 4. MDC File Validation
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4/4 MDC File Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if bash "$SCRIPT_DIR/validate-mdc.sh"; then
    echo "✅ MDC file validation passed"
else
    echo "⚠️  MDC file validation completed with warnings"
    TOTAL_WARNINGS=$((TOTAL_WARNINGS + 1))
fi
echo ""

# ============================================================================
# Summary
# ============================================================================
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Validation Suite Summary                                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

if [ $TOTAL_ERRORS -eq 0 ] && [ $TOTAL_WARNINGS -eq 0 ]; then
    echo "✅ All validation checks passed!"
    echo ""
    exit 0
elif [ $TOTAL_ERRORS -eq 0 ]; then
    echo "⚠️  Validation completed with $TOTAL_WARNINGS warning(s)"
    echo ""
    exit 0
else
    echo "❌ Validation failed with $TOTAL_ERRORS error(s) and $TOTAL_WARNINGS warning(s)"
    echo ""
    exit 1
fi
