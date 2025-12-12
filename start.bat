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

echo 🌐 App is running as a unified service...
echo.
echo ✅ QIE Nexus is now running!
echo.
echo 📍 Access the App:   http://127.0.0.1:5001
echo.
echo 🦊 MetaMask will work properly on http://127.0.0.1:5001
echo.
echo Press any key to exit...
pause > nul
