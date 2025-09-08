@echo off
REM Script para iniciar todos los microservicios
echo ======================================
echo  INICIANDO MICROSERVICIOS INDIVIDUALES
echo ======================================

echo.
echo [1/5] Iniciando Core Service (Puerto 8001)...
start "Core Service" /D "microservices\core-service" python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
timeout /t 3 /nobreak >nul

echo [2/5] Iniciando Stock Service (Puerto 8002)...
start "Stock Service" /D "microservices\stock-service" python -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload
timeout /t 3 /nobreak >nul

echo [3/5] Iniciando Obras Service (Puerto 8003)...
start "Obras Service" /D "microservices\obras-service" python -m uvicorn main:app --host 0.0.0.0 --port 8003 --reload
timeout /t 3 /nobreak >nul

echo [4/5] Iniciando Tickets Service (Puerto 8004)...
start "Tickets Service" /D "microservices\tickets-service" python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload
timeout /t 3 /nobreak >nul

echo [5/5] Esperando que los servicios estén listos...
timeout /t 10 /nobreak >nul

echo.
echo ✅ TODOS LOS SERVICIOS INICIADOS
echo.
echo 📊 URLs de los Servicios:
echo    Core Service:    http://localhost:8001/core/docs
echo    Stock Service:   http://localhost:8002/stock/docs  
echo    Obras Service:   http://localhost:8003/obras/docs
echo    Tickets Service: http://localhost:8004/tickets/docs
echo.
echo 📋 Dashboard: file:///microservices/dashboard.html
echo.
echo Presiona cualquier tecla para abrir el dashboard...
pause >nul

REM Abrir dashboard en navegador
start "" "microservices\dashboard.html"

echo.
echo ✨ Sistema de microservicios activo!
pause
