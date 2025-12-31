# IT Support Assistant - Start Script

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Starting IT Support Technical Assistant" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Start Backend
Write-Host "Starting Backend Server..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD\backend
    .\venv\Scripts\Activate.ps1
    uvicorn api.main:app --host 0.0.0.0 --port 8000
}

Write-Host "Backend starting on http://localhost:8000" -ForegroundColor Green
Write-Host "Job ID: $($backendJob.Id)" -ForegroundColor Gray

# Wait a bit for backend to start
Start-Sleep -Seconds 5

# Start Frontend
Write-Host "`nStarting Frontend Server..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD\frontend
    npm run dev
}

Write-Host "Frontend starting on http://localhost:3000" -ForegroundColor Green
Write-Host "Job ID: $($frontendJob.Id)" -ForegroundColor Gray

Write-Host "`n============================================" -ForegroundColor Green
Write-Host "Application Started!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green

Write-Host "`nAccess the application:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "  API Documentation: http://localhost:8000/docs" -ForegroundColor Yellow

Write-Host "`nMonitoring logs..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Gray
Write-Host ""

# Monitor jobs
try {
    while ($true) {
        Start-Sleep -Seconds 2
        
        # Check if jobs are still running
        if ($backendJob.State -ne "Running") {
            Write-Host "`nBackend job stopped!" -ForegroundColor Red
            Receive-Job $backendJob
            break
        }
        
        if ($frontendJob.State -ne "Running") {
            Write-Host "`nFrontend job stopped!" -ForegroundColor Red
            Receive-Job $frontendJob
            break
        }
    }
}
finally {
    Write-Host "`nStopping servers..." -ForegroundColor Yellow
    Stop-Job $backendJob
    Stop-Job $frontendJob
    Remove-Job $backendJob
    Remove-Job $frontendJob
    Write-Host "Servers stopped." -ForegroundColor Green
}
