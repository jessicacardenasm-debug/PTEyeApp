@echo off
echo ========================================
echo   OcularGuard - Iniciando servidores
echo ========================================

echo.
echo [1/2] Iniciando Backend (puerto 8000)...
start "OcularGuard Backend" cmd /k "cd /d "%~dp0backend" && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

timeout /t 2 /nobreak >nul

echo [2/2] Iniciando Frontend (puerto 5500)...
start "OcularGuard Frontend" cmd /k "cd /d "%~dp0frontend" && python -m http.server 5500"

timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   Abriendo app en el browser...
echo ========================================
start http://localhost:5500/pages/login.html

echo.
echo Servidores corriendo:
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5500
echo   API Docs: http://localhost:8000/docs
echo.
pause
