# Simple Run Script - IT Support Assistant
# Runs backend + frontend locally (no Docker)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "IT Support Assistant - Local Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$ErrorActionPreference = 'Stop'

# First-time setup
if (-not (Test-Path "backend\venv")) {
    Write-Host "" 
    Write-Host "First time setup detected." -ForegroundColor Yellow
    Write-Host "Running setup-simple.ps1..." -ForegroundColor Yellow
    .\setup-simple.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "" 
        Write-Host "Setup failed. Fix errors and re-run." -ForegroundColor Red
        exit 1
    }
}

# Ensure backend .env exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "" 
    Write-Host "WARNING: backend\.env not found." -ForegroundColor Yellow
    Write-Host "Creating from backend\.env.example..." -ForegroundColor Yellow
    Copy-Item "backend\.env.example" "backend\.env" -Force
    Write-Host "" 
    Write-Host "Add your API key in backend\.env, then continue." -ForegroundColor Yellow
    Read-Host "Press Enter to open backend\\.env in Notepad"
    notepad "backend\.env"
    Read-Host "Press Enter to continue"
}

Write-Host "" 
Write-Host "Starting services..." -ForegroundColor Green

# Kill any existing processes on these ports (best-effort)
Write-Host "" 
Write-Host "Cleaning up old processes on ports 8000 and 3000..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}
Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2

# Start backend in a new PowerShell window
Write-Host "" 
Write-Host "[1/2] Starting backend (http://localhost:8000)..." -ForegroundColor Cyan
$backendPath = Join-Path $PSScriptRoot "backend"
$backendPython = Join-Path $backendPath "venv\Scripts\python.exe"
if (-not (Test-Path $backendPython)) {
    Write-Host "Backend venv not found at backend\\venv. Run setup-simple.ps1 first." -ForegroundColor Red
    exit 1
}

# Validate venv Python version (many deps don't support 3.13+ yet)
$backendPyVersionRaw = (& $backendPython --version 2>&1).ToString().Trim()
if ($backendPyVersionRaw -match 'Python\s+(\d+)\.(\d+)\.(\d+)') {
    $pyMajor = [int]$Matches[1]
    $pyMinor = [int]$Matches[2]
    if ($pyMajor -eq 3 -and $pyMinor -ge 13) {
        Write-Host "" 
        Write-Host "ERROR: backend\\venv was created with $backendPyVersionRaw." -ForegroundColor Red
        Write-Host "This project expects Python 3.11 (recommended) or 3.12; some requirements may fail on 3.13+." -ForegroundColor Yellow
        Write-Host "Fix: install Python 3.11/3.12, then re-run: .\setup-simple.ps1" -ForegroundColor Yellow
        exit 1
    }
}

# Ensure backend deps are installed (otherwise backend window exits immediately)
try {
    & $backendPython -c "import uvicorn" | Out-Null
} catch {
    Write-Host "Backend dependencies missing. Installing from backend\\requirements.txt..." -ForegroundColor Yellow
    & $backendPython -m pip install --upgrade pip
    & $backendPython -m pip install -r (Join-Path $backendPath "requirements.txt")
}

$backendCmd = "Set-Location -LiteralPath '$backendPath'; Write-Host 'Backend server starting...' -ForegroundColor Green; & '$backendPython' -m uvicorn api.main:app --host 0.0.0.0 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $backendCmd

Write-Host "Waiting for backend to start..." -ForegroundColor Gray
Start-Sleep -Seconds 8

# Best-effort health check (with a few retries)
Write-Host "Testing backend /health..." -ForegroundColor Gray
$backendOk = $false
for ($i = 1; $i -le 10; $i++) {
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 3 -UseBasicParsing
        $backendOk = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}

if ($backendOk) {
    Write-Host "Backend is running." -ForegroundColor Green
} else {
    Write-Host "Backend is not reachable on http://localhost:8000." -ForegroundColor Red
    Write-Host "Check the backend window for the actual error (common causes: missing deps, incompatible Python, missing VC++ build tools)." -ForegroundColor Yellow
}

# Start frontend in a new PowerShell window
Write-Host "" 
Write-Host "[2/2] Starting frontend (http://localhost:3000)..." -ForegroundColor Cyan
$frontendPath = Join-Path $PSScriptRoot "frontend"
$frontendCmd = "Set-Location -LiteralPath '$frontendPath'; Write-Host 'Frontend server starting...' -ForegroundColor Green; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $frontendCmd

Start-Sleep -Seconds 2

Write-Host "" 
Write-Host "========================================" -ForegroundColor Green
Write-Host "Application started." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "" 
Write-Host "Open: http://localhost:3000" -ForegroundColor Yellow
Write-Host "API:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "Docs: http://localhost:8000/docs" -ForegroundColor Yellow

Write-Host "" 
Write-Host "To stop: close the two server windows." -ForegroundColor Yellow
Read-Host "Press Enter to close this window"
