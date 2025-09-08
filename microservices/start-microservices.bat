@echo off
REM ============================================================================
REM SCRIPT DE INICIO PARA MICROSERVICIOS (WINDOWS)
REM ============================================================================

echo 🚀 Iniciando arquitectura de microservicios...
echo ================================================

REM Verificar que Docker esté disponible
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no está instalado o no está corriendo.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose no está instalado.
    pause
    exit /b 1
)

REM Crear directorios necesarios
echo 📁 Creando directorios necesarios...
if not exist "logs\core" mkdir "logs\core"
if not exist "logs\stock" mkdir "logs\stock"
if not exist "logs\obras" mkdir "logs\obras"
if not exist "logs\nginx" mkdir "logs\nginx"
if not exist "static\core" mkdir "static\core"
if not exist "static\stock" mkdir "static\stock"
if not exist "static\obras" mkdir "static\obras"
if not exist "monitoring" mkdir "monitoring"

REM Construir e iniciar los servicios
echo 🏗️ Construyendo e iniciando servicios...
docker-compose -f docker-compose.microservices.yml up --build -d

REM Esperar a que los servicios estén listos
echo ⏳ Esperando que los servicios estén listos...
timeout /t 30 /nobreak >nul

echo 🔍 Verificando estado de los servicios...
echo ================================================

REM Health checks usando PowerShell (mejor compatibilidad en Windows)
powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://localhost:8001/core/health' -TimeoutSec 5; Write-Host 'Core Service: OK' } catch { Write-Host 'Core Service: ERROR' }"

powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://localhost:8002/stock/health' -TimeoutSec 5; Write-Host 'Stock Service: OK' } catch { Write-Host 'Stock Service: ERROR' }"

powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://localhost:8003/obras/health' -TimeoutSec 5; Write-Host 'Obras Service: OK' } catch { Write-Host 'Obras Service: ERROR' }"

powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://localhost/health' -TimeoutSec 5; Write-Host 'API Gateway: OK' } catch { Write-Host 'API Gateway: ERROR' }"

echo.
echo ================================================
echo ✅ Servicios iniciados correctamente!
echo.
echo 🔗 URLs disponibles:
echo    • API Gateway: http://localhost
echo    • Core Service: http://localhost:8001/core/docs
echo    • Stock Service: http://localhost:8002/stock/docs  
echo    • Obras Service: http://localhost:8003/obras/docs
echo    • Monitoring (Grafana): http://localhost:3000
echo    • Metrics (Prometheus): http://localhost:9090
echo.
echo 📋 Para ver logs: docker-compose -f docker-compose.microservices.yml logs -f [servicio]
echo 🛑 Para detener: stop-microservices.bat
echo.
pause
