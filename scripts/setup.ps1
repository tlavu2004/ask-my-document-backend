# scripts/setup.ps1
# ====================================================================
# Script to prepare the FastAPI development environment
# Can be run from anywhere; will switch to project root automatically.
# ====================================================================

Write-Host "Starting environment setup..." -ForegroundColor Cyan

# 0. Move to project root (one level up from scripts/)
Set-Location "$PSScriptRoot\.."

# 1. Create virtual environment
python -m venv .venv

# 2. Allow running scripts for this session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# 3. Activate the virtual environment
. .\.venv\Scripts\Activate.ps1

# 4. (Optional) Upgrade pip
python -m pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt

# 6. Fetch environment variables from .env file
$envFile = ".env"
$envValue = "unknown"
if (Test-Path $envFile) {
    $lines = Get-Content $envFile
    foreach ($line in $lines) {
        if ($line -match "^APP_ENV\s*=\s*(.+)$") {
            $envValue = $Matches[1]
            break
        }
    }
}

Write-Host "Environment setup completed! Current APP_ENV: $envValue" -ForegroundColor Green

# 7. (Optional) Start FastAPI server in development mode
Write-Host "Starting FastAPI server..." -ForegroundColor Yellow
uvicorn app.main:app --reload
