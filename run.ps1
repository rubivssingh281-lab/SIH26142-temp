# ==============================================================================
#  भू DRISTI — AI Super-Resolution Platform
#  PowerShell Runner for Windows (Backend + Frontend)
# ==============================================================================

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = $ScriptDir
$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "frontend"
$LogsDir = Join-Path $RootDir "logs"

if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir | Out-Null
}

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "          भू DRISTI — AI Super-Resolution Platform Runner" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "[INFO] Project root: $RootDir" -ForegroundColor Gray

# 1. Locate Python
$PythonBin = $null
$CandidatePythons = @(
    (Join-Path $BackendDir ".venv\Scripts\python.exe"),
    (Join-Path $BackendDir "venv\Scripts\python.exe")
)

foreach ($cand in $CandidatePythons) {
    if (Test-Path $cand) {
        $PythonBin = $cand
        break
    }
}

if (-not $PythonBin) {
    $SysPython = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($SysPython) {
        $PythonBin = $SysPython.Source
    }
}

if (-not $PythonBin) {
    Write-Host "[ERROR] Python was not found! Please install Python 3.10+." -ForegroundColor Red
    exit 1
}

$PyVer = & $PythonBin --version 2>&1
Write-Host "[OK] Using Python: $PyVer" -ForegroundColor Green

# 2. Locate npm
$NpmCmd = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $NpmCmd) {
    $NpmCmd = Get-Command npm -ErrorAction SilentlyContinue
}

if (-not $NpmCmd) {
    Write-Host "[ERROR] npm was not found! Please install Node.js 18+ LTS." -ForegroundColor Red
    exit 1
}

$NpmVer = & $NpmCmd.Source -v 2>&1
Write-Host "[OK] Using npm: $NpmVer" -ForegroundColor Green

# Ensure frontend .env.local exists
$FrontendEnv = Join-Path $FrontendDir ".env.local"
if (-not (Test-Path $FrontendEnv)) {
    $FrontendEnvExample = Join-Path $FrontendDir ".env.local.example"
    if (Test-Path $FrontendEnvExample) {
        Copy-Item $FrontendEnvExample $FrontendEnv
    } else {
        Set-Content -Path $FrontendEnv -Value "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000"
    }
    Write-Host "[INFO] Created frontend/.env.local" -ForegroundColor Gray
}

# 3. Start Backend
Write-Host "`n[INFO] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Gray
$BackendLog = Join-Path $LogsDir "backend.log"
$BackendProcess = Start-Process -FilePath $PythonBin `
    -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" `
    -WorkingDirectory $BackendDir `
    -RedirectStandardOutput $BackendLog `
    -RedirectStandardError $BackendLog `
    -PassThru

Write-Host "[OK] Backend started with PID: $($BackendProcess.Id)" -ForegroundColor Green

# 4. Start Frontend
Write-Host "[INFO] Starting Next.js Frontend on http://localhost:3000..." -ForegroundColor Gray
$FrontendLog = Join-Path $LogsDir "frontend.log"
$FrontendProcess = Start-Process -FilePath $NpmCmd.Source `
    -ArgumentList "run dev" `
    -WorkingDirectory $FrontendDir `
    -RedirectStandardOutput $FrontendLog `
    -RedirectStandardError $FrontendLog `
    -PassThru

Write-Host "[OK] Frontend started with PID: $($FrontendProcess.Id)" -ForegroundColor Green

# 5. Cleanup on exit
function Stop-BhuDristi {
    Write-Host "`n[INFO] Shutting down services..." -ForegroundColor Yellow
    if ($BackendProcess -and (-not $BackendProcess.HasExited)) {
        Stop-Process -Id $BackendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    if ($FrontendProcess -and (-not $FrontendProcess.HasExited)) {
        Stop-Process -Id $FrontendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "[OK] All services stopped." -ForegroundColor Green
}

# 6. Wait for health
Write-Host "`n[INFO] Waiting for services to become ready..." -ForegroundColor Gray
$BackendReady = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $res = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing -TimeoutSec 2
        if ($res.StatusCode -eq 200) {
            $BackendReady = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

$FrontendReady = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        $res = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 2
        if ($res.StatusCode -eq 200) {
            $FrontendReady = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

Write-Host "`n======================================================================" -ForegroundColor Green
Write-Host "          भू DRISTI IS UP AND RUNNING SUCCESSFULLY!       " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "  Frontend UI      : http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend API Docs : http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Backend Base URL : http://localhost:8000" -ForegroundColor Cyan
Write-Host "----------------------------------------------------------------------"
Write-Host "  Backend PID  : $($BackendProcess.Id)"
Write-Host "  Frontend PID : $($FrontendProcess.Id)"
Write-Host "----------------------------------------------------------------------"
Write-Host "  Press Ctrl+C to stop all services." -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Green

try {
    while ((-not $BackendProcess.HasExited) -and (-not $FrontendProcess.HasExited)) {
        Start-Sleep -Seconds 1
    }
} finally {
    Stop-BhuDristi
}
