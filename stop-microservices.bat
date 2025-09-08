@echo off
REM Script para detener todos los microservicios
echo ======================================
echo  DETENIENDO MICROSERVICIOS
echo ======================================

echo.
echo 🛑 Deteniendo servicios Python...

REM Detener procesos Python que puedan estar ejecutando los servicios
taskkill /F /IM python.exe 2>nul
taskkill /F /IM uvicorn.exe 2>nul

echo 🛑 Liberando puertos...

REM Liberar puertos específicos si están en uso
for %%p in (8001 8002 8003 8004) do (
    echo Verificando puerto %%p...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%%p') do taskkill /F /PID %%a 2>nul
)

echo.
echo 🐳 Deteniendo servicios Docker (si existen)...
docker-compose -f docker-compose.microservices.yml down 2>nul

echo.
echo ✅ TODOS LOS SERVICIOS DETENIDOS
echo.
echo Los siguientes procesos han sido terminados:
echo   - Servicios FastAPI/Uvicorn
echo   - Contenedores Docker
echo   - Procesos en puertos 8001-8004
echo.
pause
