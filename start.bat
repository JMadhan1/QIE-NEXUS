@echo off
title QIE Nexus - Complete Startup
color 0D

echo.
echo ========================================
echo    🔮 QIE Nexus - Quick Start
echo ========================================
echo.

echo ⚡ Starting Backend API Server...
start "QIE Nexus Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && python app.py"

echo ⏳ Waiting for backend to initialize...
timeout /t 2 /nobreak > nul

echo 🌐 Starting Frontend HTTP Server...
start "QIE Nexus Frontend" cmd /k "cd /d %~dp0 && python serve.py"

echo ⏳ Waiting for frontend server...
timeout /t 2 /nobreak > nul

echo.
echo ✅ QIE Nexus is now running!
echo.
echo 📍 Backend API:  http://127.0.0.1:5000
echo 📍 Frontend:     http://localhost:8080
echo 📍 Dashboard:    http://localhost:8080/dashboard.html
echo.
echo 🦊 MetaMask will work properly on http://localhost:8080
echo.
echo Press any key to exit...
pause > nul
