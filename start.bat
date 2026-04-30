@echo off
REM AgentOS Startup Script for Windows
REM Starts both backend and frontend services

echo ========================================
echo   AgentOS Startup Script
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "backend\main.py" (
    echo ERROR: backend\main.py not found!
    echo Please run this script from the agentos root directory
    pause
    exit /b 1
)

echo [1/2] Starting Backend Server (Port 8000)...
echo.
start "AgentOS Backend" cmd /k "cd backend && python main.py"

REM Wait a bit for backend to start
timeout /t 5 /nobreak > nul

echo.
echo [2/2] Starting Frontend (Port 3000)...
echo.
start "AgentOS Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo   Services Starting...
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Two new windows have opened:
echo   - AgentOS Backend (keep this running)
echo   - AgentOS Frontend (keep this running)
echo.
echo Press any key to exit this window (services will keep running)
echo To stop services: Close the respective windows or press Ctrl+C
echo ========================================
pause
