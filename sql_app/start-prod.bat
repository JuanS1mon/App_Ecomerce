@echo off
REM ==========================================
REM SCRIPT PARA PRODUCCIÓN CON DOCKER
REM ==========================================

echo.
echo ===================================
echo   PRODUCCIÓN - SQL APP
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

REM Verificar archivo de ambiente
if not exist ".env.docker" (
    echo ⚠️  Advertencia: No se encontró .env.docker
    echo    Usando configuración por defecto
)

REM Construir y levantar servicios
echo.
echo 🔨 Construyendo e iniciando servicios de producción...
docker-compose up --build -d

if errorlevel 1 (
    echo ❌ Error al iniciar servicios
    pause
    exit /b 1
)

echo.
echo ✅ Servicios de producción iniciados!
echo.
echo 🌐 Aplicación disponible en: http://localhost:80
echo 🔒 HTTPS disponible en: https://localhost:443
echo 🗄️  Base de datos en: localhost:1433
echo.
echo 📋 Comandos útiles:
echo    docker-compose logs -f                    Ver logs
echo    docker-compose down                       Detener servicios
echo    docker-compose restart app               Reiniciar app
echo    docker-compose exec app bash             Entrar al contenedor
echo.

REM Verificar estado de servicios
echo 📊 Estado de servicios:
docker-compose ps

echo.
echo ✨ ¡Producción lista!
pause
