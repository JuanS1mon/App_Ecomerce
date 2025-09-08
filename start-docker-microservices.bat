@echo off
REM Script para iniciar con Docker Compose
echo ======================================
echo  INICIANDO MICROSERVICIOS CON DOCKER
echo ======================================

echo.
echo 🔍 Verificando Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no está instalado o no está en PATH
    echo Por favor instala Docker Desktop e inténtalo de nuevo
    pause
    exit /b 1
)

echo ✅ Docker encontrado
echo.

echo 🛑 Deteniendo servicios previos...
docker-compose -f docker-compose.microservices.yml down

echo.
echo 🏗️  Construyendo e iniciando servicios...
docker-compose -f docker-compose.microservices.yml up --build -d

echo.
echo ⏳ Esperando que los servicios estén listos...
timeout /t 30 /nobreak >nul

echo.
echo 🔍 Verificando estado de los servicios...
docker-compose -f docker-compose.microservices.yml ps

echo.
echo ✅ MICROSERVICIOS DOCKER INICIADOS
echo.
echo 📊 URLs de los Servicios:
echo    API Gateway:     http://localhost/
echo    Core Service:    http://localhost/core/docs
echo    Stock Service:   http://localhost/stock/docs  
echo    Obras Service:   http://localhost/obras/docs
echo    Tickets Service: http://localhost/tickets/docs
echo.
echo 📋 Dashboard:       http://localhost/dashboard.html
echo 📊 Prometheus:      http://localhost:9090
echo 📈 Grafana:         http://localhost:3000 (admin/admin123)
echo.
echo Presiona cualquier tecla para abrir el dashboard...
pause >nul

start "" "http://localhost/dashboard.html"

echo.
echo ✨ Sistema de microservicios Docker activo!
echo.
echo Para ver logs: docker-compose -f docker-compose.microservices.yml logs -f
echo Para detener:  docker-compose -f docker-compose.microservices.yml down
pause
