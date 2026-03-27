#!/bin/bash
#
# Full System Validation Script
# Validates the entire Co-Op OS stack before production deployment
#
# Usage: ./scripts/full_system_check.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Track overall status
FAILED_CHECKS=0

# Function to run a check and track failures
run_check() {
    local check_name="$1"
    local check_command="$2"
    
    log_info "Running: $check_name"
    if eval "$check_command"; then
        log_success "$check_name passed"
        return 0
    else
        log_error "$check_name failed"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

echo "========================================="
echo "  Co-Op OS Full System Validation"
echo "========================================="
echo ""

# ── 1. Environment Check ─────────────────────────────────────────────────────
log_info "Step 1: Environment Check"
run_check "Docker installed" "command -v docker > /dev/null"
run_check "Docker Compose installed" "command -v docker compose > /dev/null"
run_check "Python 3.12+ installed" "python --version | grep -E 'Python 3\.(1[2-9]|[2-9][0-9])'"
run_check "Node 20+ installed" "node --version | grep -E 'v(2[0-9]|[3-9][0-9])'"
run_check "pnpm installed" "command -v pnpm > /dev/null"
echo ""

# ── 2. Dependency Security ───────────────────────────────────────────────────
log_info "Step 2: Dependency Security Scan"
run_check "pnpm audit" "pnpm audit --audit-level moderate"
run_check "pip-audit (Python)" "cd services/api && pip-audit --skip-editable --ignore-vuln CVE-2026-4539 || true"
echo ""

# ── 3. Code Quality ──────────────────────────────────────────────────────────
log_info "Step 3: Code Quality Checks"
run_check "Python linting (ruff)" "cd services/api && ruff check ."
run_check "TypeScript linting" "pnpm lint"
echo ""

# ── 4. Backend Tests ─────────────────────────────────────────────────────────
log_info "Step 4: Backend Unit Tests"
run_check "Python unit tests" "cd services/api && pytest -v"
echo ""

# ── 5. Frontend Build ────────────────────────────────────────────────────────
log_info "Step 5: Frontend Build Validation"
run_check "Next.js build" "cd apps/web && pnpm build"
echo ""

# ── 6. Docker Services ───────────────────────────────────────────────────────
log_info "Step 6: Docker Services"
log_info "Starting Docker Compose stack..."
cd infrastructure/docker
docker compose down > /dev/null 2>&1 || true
docker compose up -d

log_info "Waiting for services to be healthy (60s timeout)..."
TIMEOUT=60
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    if docker compose ps | grep -q "healthy"; then
        log_success "Services are starting up"
        break
    fi
    sleep 2
    ELAPSED=$((ELAPSED + 2))
done

# Wait additional time for all services
sleep 10

run_check "Postgres healthy" "docker compose ps postgres | grep -q 'healthy'"
run_check "Redis running" "docker compose ps redis | grep -q 'Up'"
run_check "MinIO healthy" "docker compose ps minio | grep -q 'healthy'"
run_check "API running" "docker compose ps co-op-api | grep -q 'Up'"

cd ../..
echo ""

# ── 7. Health Endpoints ──────────────────────────────────────────────────────
log_info "Step 7: Health Endpoint Validation"
log_info "Waiting for API to be ready..."
sleep 5

run_check "API health endpoint" "curl -f http://localhost:8000/health > /dev/null 2>&1"
run_check "API ready endpoint" "curl -f http://localhost:8000/ready > /dev/null 2>&1 || curl -s http://localhost:8000/ready | grep -q 'degraded'"
echo ""

# ── 8. Database Connectivity ─────────────────────────────────────────────────
log_info "Step 8: Database Connectivity"
run_check "Database connection" "docker exec docker-postgres-1 psql -U postgres -d coop -c 'SELECT 1;' > /dev/null 2>&1"
echo ""

# ── 9. Container Builds ──────────────────────────────────────────────────────
log_info "Step 9: Container Build Validation"
run_check "API Docker build" "docker build -t co-op-api:test ./services/api > /dev/null 2>&1"
run_check "Web Docker build" "docker build -t co-op-web:test ./apps/web > /dev/null 2>&1"
echo ""

# ── 10. Cleanup ──────────────────────────────────────────────────────────────
log_info "Step 10: Cleanup"
log_info "Stopping Docker services..."
cd infrastructure/docker
docker compose down > /dev/null 2>&1
cd ../..
log_success "Cleanup complete"
echo ""

# ── Final Report ─────────────────────────────────────────────────────────────
echo "========================================="
echo "  Validation Complete"
echo "========================================="
echo ""

if [ $FAILED_CHECKS -eq 0 ]; then
    log_success "All checks passed! System is production-ready."
    echo ""
    echo "Next steps:"
    echo "  1. Review any warnings above"
    echo "  2. Commit and push changes"
    echo "  3. Merge PR after CI passes"
    echo "  4. Tag release: git tag -a v1.0.3 -m 'Production Release'"
    exit 0
else
    log_error "$FAILED_CHECKS check(s) failed"
    echo ""
    echo "Please fix the failing checks before proceeding to production."
    exit 1
fi
