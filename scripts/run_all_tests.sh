#!/bin/bash
set -e

echo "=== Co-Op v1.0 Test Runner ==="
echo ""

echo "1. Running Backend Tests..."
cd services/api
python -m pytest tests/ -v --tb=short | tee ../../TEST_REPORT.md
PYTEST_EXIT=$?
cd ../..
echo ""

echo "2. Checking Frontend Build..."
if [ -d "apps/web" ]; then
    cd apps/web
    pnpm build
    BUILD_EXIT=$?
    cd ../..
else
    echo "apps/web directory not found, skipping frontend build."
    BUILD_EXIT=0
fi
echo ""

echo "=== Tests Complete ==="
if [ $PYTEST_EXIT -ne 0 ]; then
    echo "Backend tests failed with exit code $PYTEST_EXIT"
fi
if [ $BUILD_EXIT -ne 0 ]; then
    echo "Frontend build failed with exit code $BUILD_EXIT"
fi

if [ $PYTEST_EXIT -eq 0 ] && [ $BUILD_EXIT -eq 0 ]; then
    echo "All tests passed successfully!"
    exit 0
else
    exit 1
fi
