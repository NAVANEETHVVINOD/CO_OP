Write-Host "=== Co-Op v1.0 Test Runner ===" -ForegroundColor Green
Write-Host ""

Write-Host "1. Running Backend Tests..." -ForegroundColor Cyan
Set-Location services/api
python -m pytest tests/ -v --tb=short | Tee-Object -FilePath "../../TEST_REPORT.md"
$pytestExit = $LASTEXITCODE
Set-Location ../../
Write-Host ""

Write-Host "2. Checking Frontend Build..." -ForegroundColor Cyan
if (Test-Path "apps/web") {
    Set-Location apps/web
    pnpm build
    $buildExit = $LASTEXITCODE
    Set-Location ../../
} else {
    Write-Host "apps/web directory not found, skipping frontend build." -ForegroundColor Yellow
    $buildExit = 0
}
Write-Host ""

Write-Host "=== Tests Complete ===" -ForegroundColor Green
if ($pytestExit -ne 0) {
    Write-Host "Backend tests failed with exit code $pytestExit" -ForegroundColor Red
}
if ($buildExit -ne 0) {
    Write-Host "Frontend build failed with exit code $buildExit" -ForegroundColor Red
}

if ($pytestExit -eq 0 -and $buildExit -eq 0) {
    Write-Host "All tests passed successfully!" -ForegroundColor Green
    exit 0
} else {
    exit 1
}
