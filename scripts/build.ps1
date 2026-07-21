# Atlas Standalone Installer Builder Script

Write-Host "=========================================="
Write-Host "     ATLAS COMPILATION PIPELINE           "
Write-Host "=========================================="

# 1. Compile React Frontend
Write-Host "[1/5] Compiling React static assets..."
npm run build --prefix frontend

# 2. Compile Electron Main Process TypeScript
Write-Host "[2/5] Compiling Electron main TypeScript scripts..."
npm run build --prefix desktop

# 3. Compile Python FastAPI Backend into Standalone Binary
Write-Host "[3/5] Packaging Python Backend using PyInstaller..."
cd backend
.\venv\Scripts\pyinstaller --clean --onefile --noconsole --name=atlas-backend app/main.py
cd ..

# 4. Copy backend binary to desktop resources
Write-Host "[4/5] Copying compiled backend binary to Electron assets..."
$null = New-Item -ItemType Directory -Force -Path "desktop/resources/bin"
Copy-Item -Path "backend/dist/atlas-backend.exe" -Destination "desktop/resources/bin/atlas-backend.exe" -Force

# 5. Package Electron Desktop Installer
Write-Host "[5/5] Packaging Electron application installer..."
cd desktop
npx electron-builder build --win --dir
cd ..

Write-Host "=========================================="
Write-Host "   SUCCESS: COMPILATION COMPLETED         "
Write-Host "=========================================="
