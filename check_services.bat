@echo off
REM Quick health check for AgentOS services

echo Checking AgentOS Services...
echo.

echo [Backend - Port 8000]
curl -s http://localhost:8000 >nul 2>&1
if %errorlevel% equ 0 (
    echo   Status: RUNNING
    curl -s http://localhost:8000 2>nul
) else (
    echo   Status: NOT RUNNING
    echo   Start with: cd backend ^&^& python main.py
)

echo.
echo [Frontend - Port 3000]
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo   Status: RUNNING
) else (
    echo   Status: NOT RUNNING
    echo   Start with: cd frontend ^&^& npm run dev
)

echo.
echo ========================================
pause
