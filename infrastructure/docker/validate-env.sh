#!/bin/bash
# ============================================================================
# Co-Op OS v1.0.3 Environment Validation Script
# ============================================================================
# This script validates that all required environment variables are set
# in the .env file before starting Docker services.
#
# Usage:
#   bash infrastructure/docker/validate-env.sh [path-to-env-file]
#
# Example:
#   bash infrastructure/docker/validate-env.sh infrastructure/docker/.env
# ============================================================================

set -e

# Default to .env in the same directory as this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${1:-$SCRIPT_DIR/.env}"

echo "Co-Op OS v1.0.3 - Environment Validation"
echo "========================================"
echo ""

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: Environment file not found: $ENV_FILE"
    echo ""
    echo "Please create a .env file from .env.example:"
    echo "  cp $SCRIPT_DIR/.env.example $SCRIPT_DIR/.env"
    echo ""
    exit 1
fi

echo "✓ Found environment file: $ENV_FILE"
echo ""

# Required environment variables
REQUIRED_VARS=(
    "DB_PASS"
    "MINIO_ROOT_USER"
    "MINIO_ROOT_PASSWORD"
    "SECRET_KEY"
    "OLLAMA_URL"
    "API_BASE_URL"
    "FRONTEND_URL"
    "LITELLM_URL"
    "REDIS_URL"
    "MINIO_URL"
    "ENVIRONMENT"
    "NEXT_PUBLIC_API_URL"
)

# Source the .env file
set -a
source "$ENV_FILE"
set +a

# Check for missing variables
MISSING=()
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING+=("$var")
    fi
done

# Report results
if [ ${#MISSING[@]} -gt 0 ]; then
    echo "❌ Error: Missing required environment variables:"
    echo ""
    for var in "${MISSING[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "Please set these variables in $ENV_FILE"
    echo "Refer to $SCRIPT_DIR/.env.example for guidance"
    echo ""
    exit 1
fi

# Validate SECRET_KEY length
if [ ${#SECRET_KEY} -lt 32 ]; then
    echo "❌ Error: SECRET_KEY must be at least 32 characters long"
    echo "   Current length: ${#SECRET_KEY}"
    echo ""
    echo "Please update SECRET_KEY in $ENV_FILE"
    echo ""
    exit 1
fi

# Validate ENVIRONMENT value
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    echo "⚠️  Warning: ENVIRONMENT should be one of: development, staging, production"
    echo "   Current value: $ENVIRONMENT"
    echo ""
fi

# All checks passed
echo "✅ All required environment variables are set"
echo ""
echo "Configuration summary:"
echo "  Environment:     $ENVIRONMENT"
echo "  Database:        ${DATABASE_URL%%@*}@***"
echo "  Redis:           $REDIS_URL"
echo "  MinIO:           $MINIO_URL"
echo "  API URL:         $API_BASE_URL"
echo "  Frontend URL:    $FRONTEND_URL"
echo "  Public API URL:  $NEXT_PUBLIC_API_URL"
echo ""
echo "✓ Ready to start Docker services"
echo ""
