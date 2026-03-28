# Check PR Status Script
# Usage: .\scripts\check-pr-status.ps1 [PR_NUMBER]
# Example: .\scripts\check-pr-status.ps1 7

param(
    [Parameter(Mandatory=$false)]
    [int]$PRNumber = 7
)

$headers = @{'Accept'='application/vnd.github.v3+json'}
$repo = "NAVANEETHVVINOD/CO_OP"

try {
    Write-Host "Fetching PR #$PRNumber status..." -ForegroundColor Cyan
    
    $pr = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/pulls/$PRNumber" -Headers $headers
    $checks = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/commits/$($pr.head.sha)/check-runs" -Headers $headers
    
    Write-Host "`n================================================================" -ForegroundColor Cyan
    Write-Host "  PR #$PRNumber Status Summary" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "Title:     $($pr.title)"
    Write-Host "State:     $($pr.state)"
    Write-Host "Mergeable: $($pr.mergeable_state)"
    Write-Host "Head SHA:  $($pr.head.sha)"
    Write-Host "Branch:    $($pr.head.ref)"
    
    Write-Host "`n================================================================" -ForegroundColor Cyan
    Write-Host "  Check Results" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    
    foreach ($check in $checks.check_runs) {
        $icon = "⏳"
        if ($check.conclusion -eq "success") { $icon = "✅" }
        elseif ($check.conclusion -eq "failure") { $icon = "❌" }
        elseif ($check.conclusion -eq "cancelled") { $icon = "⚠️" }
        elseif ($check.status -eq "in_progress") { $icon = "🔄" }
        
        $status = if ($check.conclusion) { $check.conclusion } else { $check.status }
        Write-Host "$icon $($check.name): $status"
    }
    
    $failed = $checks.check_runs | Where-Object {$_.conclusion -eq 'failure'}
    if ($failed) {
        Write-Host "`n================================================================" -ForegroundColor Red
        Write-Host "  Failed Checks" -ForegroundColor Red
        Write-Host "================================================================" -ForegroundColor Red
        foreach ($f in $failed) {
            Write-Host "❌ $($f.name)" -ForegroundColor Red
            Write-Host "   URL: $($f.html_url)" -ForegroundColor Gray
        }
    }
    else {
        $inProgress = $checks.check_runs | Where-Object {$_.status -ne 'completed'}
        if ($inProgress) {
            Write-Host "`n⏳ $($inProgress.Count) check(s) still in progress..." -ForegroundColor Yellow
        }
        else {
            Write-Host "`n✅ All checks passed!" -ForegroundColor Green
        }
    }
    
    Write-Host "`nPR URL: $($pr.html_url)" -ForegroundColor Cyan
    
}
catch {
    Write-Host "Error fetching PR status: $_" -ForegroundColor Red
    exit 1
}
