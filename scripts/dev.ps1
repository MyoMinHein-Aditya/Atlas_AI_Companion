# Atlas Dev Launch Script

Write-Host "==========================================" -ForegroundColor Magenta
Write-Host "   ATLAS DEVELOPMENT SYSTEM LAUNCHER   " -ForegroundColor Magenta
Write-Host "==========================================" -ForegroundColor Magenta

# 1. Spin up the Vite React Frontend Dev Server in a dedicated PowerShell window
Write-Host "[1/3] Spinning up Frontend Dev Server in new window..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot\..\frontend'; npm run dev"

# 2. Wait 3 seconds to let the Vite server bind to port 5173
Start-Sleep -Seconds 3

# 3. Launch Electron main process (which builds desktop TS and spawns FastAPI backend)
Write-Host "[2/3] Building Electron main & launching App..." -ForegroundColor Cyan
npm start --prefix desktop

Write-Host "[3/3] Shutdown complete." -ForegroundColor Green
