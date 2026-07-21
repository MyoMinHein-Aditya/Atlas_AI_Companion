# Atlas Dev Launch Script

Write-Host "==========================================" -ForegroundColor Magenta
Write-Host "   ATLAS DEVELOPMENT SYSTEM LAUNCHER   " -ForegroundColor Magenta
Write-Host "==========================================" -ForegroundColor Magenta

# 1. Spin up the Vite React Frontend Dev Server in a separate window
Write-Host "[1/3] Spinning up Frontend Dev Server..." -ForegroundColor Yellow
Start-Process npm -ArgumentList "run", "dev", "--prefix", "frontend"

# 2. Wait briefly to let the Vite server bind to port 5173
Start-Sleep -Seconds 3

# 3. Launch Electron, which compiles the main process and spawns the FastAPI Backend
Write-Host "[2/3] Building Electron main & launching App..." -ForegroundColor Cyan
npm start --prefix desktop

Write-Host "[3/3] Shutdown complete." -ForegroundColor Green
