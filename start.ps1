# QIE Nexus - Quick Start Script
# This script starts the backend and opens the frontend

Write-Host "🔮 Starting QIE Nexus..." -ForegroundColor Magenta
Write-Host ""

# Start Backend API Server
Write-Host "⚡ Starting Backend API Server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; .\venv\Scripts\Activate.ps1; python app.py"

# Wait for backend to start
Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Open Frontend in Browser
Write-Host "🌐 Opening QIE Nexus Website..." -ForegroundColor Green
Start-Process "file:///$PSScriptRoot/frontend/index.html"

Write-Host ""
Write-Host "✅ QIE Nexus is now running!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Backend API: http://127.0.0.1:5000" -ForegroundColor White
Write-Host "📍 Frontend: file:///$PSScriptRoot/frontend/index.html" -ForegroundColor White
Write-Host "📍 Dashboard: file:///$PSScriptRoot/frontend/dashboard.html" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
