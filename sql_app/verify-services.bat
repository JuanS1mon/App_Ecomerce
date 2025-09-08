@echo off
REM ==========================================
REM VERIFICACIÓN DE SERVICIOS DOCKER
REM ==========================================

echo.
echo ===================================
echo   VERIFICACIÓN DE SERVICIOS
echo ===================================
echo.

REM Verificar si Docker está corriendo
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no está corriendo
    exit /b 1
) else (
    echo ✅ Docker está activo
)

echo.
echo 🔍 Verificando servicios...

REM Verificar contenedores activos
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=sql_app"

echo.
echo 🌐 Verificando conectividad...

REM Verificar aplicación FastAPI
echo Probando aplicación FastAPI...
curl -s -o nul -w "HTTP Status: %%{http_code}\n" http://localhost:8000/health
if errorlevel 1 (
    echo ❌ Aplicación no responde
) else (
    echo ✅ Aplicación respondiendo
)

REM Verificar base de datos
echo.
echo Probando conexión a base de datos...
docker exec sql_app_database_1 /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "MyStrongPassword123!" -Q "SELECT 1" >nul 2>&1
if errorlevel 1 (
    echo ❌ Base de datos no responde
) else (
    echo ✅ Base de datos respondiendo
)

echo.
echo 📊 Estado detallado de contenedores:
docker-compose ps

echo.
echo 📋 Uso de recursos:
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" sql_app_fastapi sql_app_database

echo.
echo ✨ Verificación completada!
pause
