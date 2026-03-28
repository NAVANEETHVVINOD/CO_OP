#!/bin/bash

# Co-Op OS v1.0.3 - Security Scan Script
# Scans for security issues in the codebase

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Co-Op OS v1.0.3 - Security Scan${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

ERRORS=0
WARNINGS=0

# Check 1: Hardcoded secrets in Python files
echo -e "${YELLOW}Checking for hardcoded secrets in Python files...${NC}"
echo ""

SECRET_PATTERNS=(
    "password\s*=\s*['\"][^'\"]+['\"]"
    "api_key\s*=\s*['\"][^'\"]+['\"]"
    "secret\s*=\s*['\"][^'\"]+['\"]"
    "token\s*=\s*['\"][^'\"]+['\"]"
    "SECRET_KEY\s*=\s*['\"][^'\"]+['\"]"
)

for pattern in "${SECRET_PATTERNS[@]}"; do
    matches=$(grep -rn -E "$pattern" services/api/app --include="*.py" 2>/dev/null || true)
    if [ -n "$matches" ]; then
        # Filter out test files and settings with env vars
        filtered=$(echo "$matches" | grep -v "test_" | grep -v "os.getenv" | grep -v "settings\." || true)
        if [ -n "$filtered" ]; then
            echo -e "${RED}ERROR: Found potential hardcoded secret:${NC}"
            echo "$filtered"
            ((ERRORS++))
        fi
    fi
done

# Check 2: Hardcoded secrets in TypeScript files
echo -e "${YELLOW}Checking for hardcoded secrets in TypeScript files...${NC}"
echo ""

TS_SECRET_PATTERNS=(
    "password:\s*['\"][^'\"]+['\"]"
    "apiKey:\s*['\"][^'\"]+['\"]"
    "secret:\s*['\"][^'\"]+['\"]"
    "token:\s*['\"][^'\"]+['\"]"
)

for pattern in "${TS_SECRET_PATTERNS[@]}"; do
    matches=$(grep -rn -E "$pattern" apps/web/src --include="*.ts" --include="*.tsx" 2>/dev/null || true)
    if [ -n "$matches" ]; then
        # Filter out test files and env access
        filtered=$(echo "$matches" | grep -v "test" | grep -v "process.env" | grep -v "env\." || true)
        if [ -n "$filtered" ]; then
            echo -e "${RED}ERROR: Found potential hardcoded secret:${NC}"
            echo "$filtered"
            ((ERRORS++))
        fi
    fi
done

# Check 3: .env files in version control
echo -e "${YELLOW}Checking for .env files in version control...${NC}"
echo ""

ENV_FILES=$(git ls-files | grep "\.env$" | grep -v "\.env\.example" | grep -v "\.env\.template" || true)
if [ -n "$ENV_FILES" ]; then
    echo -e "${RED}ERROR: Found .env files in version control:${NC}"
    echo "$ENV_FILES"
    ((ERRORS++))
else
    echo -e "${GREEN}SUCCESS: No .env files in version control${NC}"
fi
echo ""

# Check 4: .gitignore includes .env patterns
echo -e "${YELLOW}Checking .gitignore for .env patterns...${NC}"
echo ""

if [ -f .gitignore ]; then
    if grep -q "\.env" .gitignore; then
        echo -e "${GREEN}SUCCESS: .gitignore includes .env patterns${NC}"
    else
        echo -e "${RED}ERROR: .gitignore does not include .env patterns${NC}"
        ((ERRORS++))
    fi
else
    echo -e "${RED}ERROR: .gitignore file not found${NC}"
    ((ERRORS++))
fi
echo ""

# Check 5: Hardcoded URLs not using settings
echo -e "${YELLOW}Checking for hardcoded URLs in Python files...${NC}"
echo ""

URL_PATTERNS=(
    "http://localhost:[0-9]+"
    "http://127\.0\.0\.1:[0-9]+"
)

for pattern in "${URL_PATTERNS[@]}"; do
    matches=$(grep -rn -E "$pattern" services/api/app --include="*.py" 2>/dev/null || true)
    if [ -n "$matches" ]; then
        # Filter out comments, test files, and settings usage
        filtered=$(echo "$matches" | grep -v "#" | grep -v "test_" | grep -v "settings\." | grep -v "os.getenv" || true)
        if [ -n "$filtered" ]; then
            echo -e "${YELLOW}WARNING: Found hardcoded URL (should use settings):${NC}"
            echo "$filtered"
            ((WARNINGS++))
        fi
    fi
done

# Check 6: Hardcoded URLs in TypeScript files
echo -e "${YELLOW}Checking for hardcoded URLs in TypeScript files...${NC}"
echo ""

for pattern in "${URL_PATTERNS[@]}"; do
    matches=$(grep -rn -E "$pattern" apps/web/src --include="*.ts" --include="*.tsx" 2>/dev/null || true)
    if [ -n "$matches" ]; then
        # Filter out comments and env usage
        filtered=$(echo "$matches" | grep -v "//" | grep -v "process.env" | grep -v "env\." || true)
        if [ -n "$filtered" ]; then
            echo -e "${YELLOW}WARNING: Found hardcoded URL (should use env):${NC}"
            echo "$filtered"
            ((WARNINGS++))
        fi
    fi
done

# Summary
echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Security Scan Summary${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}All security checks passed!${NC}"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}Security scan completed with $WARNINGS warning(s)${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}Security scan failed with $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    echo ""
    exit 1
fi
