# IT Support Assistant - Setup and Run Script

$ErrorActionPreference = 'Stop'

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "IT Support Technical Assistant - Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

function Get-PythonVersionObject {
    param([Parameter(Mandatory = $true)][string]$VersionString)
    if ($VersionString -match 'Python\s+(\d+)\.(\d+)\.(\d+)') {
        return [PSCustomObject]@{
            Major = [int]$Matches[1]
            Minor = [int]$Matches[2]
            Patch = [int]$Matches[3]
            Raw   = $VersionString
        }
    }
    return $null
}

Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonSelector = $null
$pyCmd = Get-Command py -ErrorAction SilentlyContinue
if ($pyCmd) {
    foreach ($minor in @(11, 12)) {
        try {
            $raw = (& py "-3.$minor" --version 2>&1).ToString().Trim()
            if ($LASTEXITCODE -eq 0) {
                $ver = Get-PythonVersionObject -VersionString $raw
                if ($ver -and $ver.Major -eq 3 -and $ver.Minor -eq $minor) {
                    $pythonSelector = [PSCustomObject]@{ Kind = 'py'; Args = @("-3.$minor"); Version = $ver }
                    break
                }
            }
        }
        catch { }
    }
}

if (-not $pythonSelector) {
    $raw = (python --version 2>&1).ToString().Trim()
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
        Write-Host "Please install Python 3.11 (recommended) or 3.12 from https://www.python.org/" -ForegroundColor Red
        exit 1
    }
    $ver = Get-PythonVersionObject -VersionString $raw
    $pythonSelector = [PSCustomObject]@{ Kind = 'python'; Args = @(); Version = $ver }
}

Write-Host "Found: $($pythonSelector.Version.Raw)" -ForegroundColor Green
if ($pythonSelector.Version -and $pythonSelector.Version.Major -eq 3 -and $pythonSelector.Version.Minor -ge 13) {
    Write-Host "ERROR: Python 3.13+ is not recommended for this project yet (some deps may require C++ build tools / may not have wheels)." -ForegroundColor Red
    Write-Host "Install Python 3.11 or 3.12, then re-run setup." -ForegroundColor Yellow
    exit 1
}

# Check Node.js version
Write-Host "`nChecking Node.js version..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js 18+ from https://nodejs.org/" -ForegroundColor Red
    exit 1
}
Write-Host "Found: Node.js $nodeVersion" -ForegroundColor Green

# Setup Backend
Write-Host "`n--------------------------------------------" -ForegroundColor Cyan
Write-Host "Setting up Backend..." -ForegroundColor Cyan
Write-Host "--------------------------------------------" -ForegroundColor Cyan

Set-Location backend

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    if ($pythonSelector.Kind -eq 'py') {
        & py @($pythonSelector.Args + @('-m', 'venv', 'venv'))
    }
    else {
        python -m venv venv
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt

# Create necessary directories
Write-Host "Creating data directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data/raw" | Out-Null
New-Item -ItemType Directory -Force -Path "data/processed" | Out-Null
New-Item -ItemType Directory -Force -Path "data/chroma_db" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "`nWARNING: .env file not found!" -ForegroundColor Yellow
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "`nIMPORTANT: Please edit backend/.env and add your API keys!" -ForegroundColor Red
    Write-Host "  - Get OpenAI API key from: https://platform.openai.com/api-keys" -ForegroundColor Cyan
    Write-Host "  - Or Anthropic API key from: https://console.anthropic.com/" -ForegroundColor Cyan
    Write-Host "`nPress any key after adding your API keys..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

Set-Location ..

# Setup Frontend
Write-Host "`n--------------------------------------------" -ForegroundColor Cyan
Write-Host "Setting up Frontend..." -ForegroundColor Cyan
Write-Host "--------------------------------------------" -ForegroundColor Cyan

Set-Location frontend

# Install dependencies
Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
npm install

Set-Location ..

# Initialize knowledge base
Write-Host "`n--------------------------------------------" -ForegroundColor Cyan
Write-Host "Initializing Knowledge Base..." -ForegroundColor Cyan
Write-Host "--------------------------------------------" -ForegroundColor Cyan

Set-Location backend
.\venv\Scripts\Activate.ps1

Write-Host "Generating sample knowledge base..." -ForegroundColor Yellow
Write-Host "(In production, run data collection and preprocessing scripts)" -ForegroundColor Gray

# The RAG service will auto-initialize with sample data on first run

Set-Location ..

Write-Host "`n============================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green

Write-Host "`nTo start the application:" -ForegroundColor Cyan
Write-Host "  1. Run: .\start.ps1" -ForegroundColor Yellow
Write-Host "  OR" -ForegroundColor Gray
Write-Host "  2. Start backend: cd backend; .\venv\Scripts\Activate.ps1; uvicorn api.main:app --reload" -ForegroundColor Yellow
Write-Host "  3. Start frontend: cd frontend; npm run dev" -ForegroundColor Yellow

Write-Host "`nAccess the application at:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor Green
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor Green

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
