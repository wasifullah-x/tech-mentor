# Quick Setup Script - First Time Only

$ErrorActionPreference = 'Stop'

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "First Time Setup - IT Support Assistant" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

function Get-PythonVersionObject {
    param(
        [Parameter(Mandatory = $true)][string]$VersionString
    )

    # Expected format: "Python 3.11.7"
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

function Get-PreferredPython {
    # Prefer Python 3.11/3.12 because core deps (e.g., torch) often lag behind latest Python.
    $pyCmd = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCmd) {
        foreach ($minor in @(11, 12)) {
            try {
                $raw = (& py "-3.$minor" --version 2>&1).ToString().Trim()
                if ($LASTEXITCODE -eq 0) {
                    $ver = Get-PythonVersionObject -VersionString $raw
                    if ($ver -and $ver.Major -eq 3 -and $ver.Minor -eq $minor) {
                        return [PSCustomObject]@{ Kind = 'py'; Args = @("-3.$minor"); Version = $ver }
                    }
                }
            }
            catch { }
        }
    }

    try {
        $raw = (python --version 2>&1).ToString().Trim()
        $ver = Get-PythonVersionObject -VersionString $raw
        if ($ver) {
            return [PSCustomObject]@{ Kind = 'python'; Args = @(); Version = $ver }
        }
    }
    catch { }

    return $null
}

# Check Python
Write-Host "`n[1/4] Checking Python..." -ForegroundColor Yellow
$preferred = Get-PreferredPython
if (-not $preferred) {
    Write-Host "Python not found!" -ForegroundColor Red
    Write-Host "Install Python 3.11 (recommended) or 3.12 from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "`nPress Enter to exit"
    exit 1
}

Write-Host "Found: $($preferred.Version.Raw)" -ForegroundColor Green
if ($preferred.Version.Major -ne 3 -or $preferred.Version.Minor -ge 13) {
    Write-Host "`nWARNING: Detected Python $($preferred.Version.Major).$($preferred.Version.Minor).$($preferred.Version.Patch)." -ForegroundColor Yellow
    Write-Host "This project is intended for Python 3.11/3.12 (some dependencies may not support 3.13+ yet)." -ForegroundColor Yellow
    Write-Host "If you have Python 3.11 installed, make sure the Windows Python Launcher (py.exe) can find it (e.g., 'py -3.11 --version'), then re-run setup." -ForegroundColor Yellow
}

# Check Node.js
Write-Host "`n[2/4] Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "Found: Node.js $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "Node.js not found!" -ForegroundColor Red
    Write-Host "Install from: https://nodejs.org/" -ForegroundColor Yellow
    Read-Host "`nPress Enter to exit"
    exit 1
}

# Setup Backend
Write-Host "`n[3/4] Setting up Backend..." -ForegroundColor Yellow
Set-Location backend

if (Test-Path "venv\Scripts\python.exe") {
    $venvRaw = (& .\venv\Scripts\python.exe --version 2>&1).ToString().Trim()
    $venvVer = Get-PythonVersionObject -VersionString $venvRaw
    if ($venvVer -and $venvVer.Major -eq 3 -and $venvVer.Minor -ge 13) {
        Write-Host "Existing backend venv uses $($venvVer.Raw). Recreating with Python 3.11/3.12..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force "venv"
    }
}

if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Gray
    if ($preferred.Kind -eq 'py') {
        & py @($preferred.Args + @('-m', 'venv', 'venv'))
    }
    else {
        python -m venv venv
    }
}

Write-Host "Installing Python packages (this may take a few minutes)..." -ForegroundColor Gray
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt

# Verify core runtime dependency is present
try {
    .\venv\Scripts\python.exe -c "import uvicorn" | Out-Null
}
catch {
    Write-Host "`nERROR: Backend dependencies did not install correctly (uvicorn missing)." -ForegroundColor Red
    Write-Host "This usually happens when your Python version is too new for one of the requirements." -ForegroundColor Yellow
    Write-Host "Install Python 3.11 (recommended) or 3.12, then re-run: .\setup-simple.ps1" -ForegroundColor Yellow
    Read-Host "`nPress Enter to exit"
    exit 1
}

Write-Host "Creating data directories..." -ForegroundColor Gray
New-Item -ItemType Directory -Force -Path "data/raw", "data/processed", "data/chroma_db", "logs" | Out-Null

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env file" -ForegroundColor Green
}

Set-Location ..

# Setup Frontend
Write-Host "`n[4/4] Setting up Frontend..." -ForegroundColor Yellow
Set-Location frontend

Write-Host "Installing Node.js packages (this may take a few minutes)..." -ForegroundColor Gray
npm install --silent

Set-Location ..

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "`nIMPORTANT: Add your OpenAI API key!" -ForegroundColor Yellow
Write-Host "`n1. Get API key from: https://platform.openai.com/api-keys" -ForegroundColor Cyan
Write-Host "2. Open: backend\.env" -ForegroundColor Cyan
Write-Host "3. Add: OPENAI_API_KEY=sk-your-key-here" -ForegroundColor Cyan

Write-Host "`nPress Enter to open .env file now..." -ForegroundColor Yellow
Read-Host
notepad "backend\.env"

Write-Host "`nAfter adding your API key, run:" -ForegroundColor Cyan
Write-Host "  .\run.ps1" -ForegroundColor Yellow

Write-Host "`nPress Enter to exit..." -ForegroundColor Gray
Read-Host
