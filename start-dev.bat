@echo off
REM ==========================================
REM SCRIPT PARA DESARROLLO CON DOCKER
REM ==========================================

echo.
echo ===================================
echo   DESARROLLO - SQL APP
echo ===================================
echo.

REM Verificar si Docker está corriendo
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker no está corriendo
    echo    Por favor, inicia Docker Desktop
    pause
    exit /b 1
)

echo ✅ Docker está corriendo

REM Construir y levantar servicios
echo.
echo 🔨 Construyendo e iniciando servicios...
docker-compose -f docker-compose.dev.yml up --build -d

if errorlevel 1 (
    echo ❌ Error al iniciar servicios
    pause
    exit /b 1
)

echo.
echo ✅ Servicios iniciados exitosamente!
echo.
echo 🌐 Aplicación disponible en: http://localhost:8000
echo 🗄️  Base de datos en: localhost:1433
echo.
echo 📋 Comandos útiles:
echo    docker-compose -f docker-compose.dev.yml logs -f        Ver logs
echo    docker-compose -f docker-compose.dev.yml down           Detener servicios
echo    docker-compose -f docker-compose.dev.yml restart app    Reiniciar app
echo.

REM Mostrar logs iniciales
echo 📊 Logs iniciales:
docker-compose -f docker-compose.dev.yml logs --tail=20

echo.
echo ✨ ¡Desarrollo listo!
pause
