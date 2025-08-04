@echo off
REM ==========================================
REM SCRIPT PARA DETENER SERVICIOS DOCKER
REM ==========================================

echo.
echo ===================================
echo   DETENIENDO SERVICIOS
echo ===================================
echo.

set /p choice="¿Qué entorno quieres detener? (d)esarrollo / (p)roducción / (a)mbos: "

if /i "%choice%"=="d" (
    echo.
    echo 🛑 Deteniendo servicios de desarrollo...
    docker-compose -f docker-compose.dev.yml down
    echo ✅ Servicios de desarrollo detenidos
)

if /i "%choice%"=="p" (
    echo.
    echo 🛑 Deteniendo servicios de producción...
    docker-compose down
    echo ✅ Servicios de producción detenidos
)

if /i "%choice%"=="a" (
    echo.
    echo 🛑 Deteniendo todos los servicios...
    docker-compose -f docker-compose.dev.yml down
    docker-compose down
    echo ✅ Todos los servicios detenidos
)

echo.
echo 🧹 ¿Quieres limpiar contenedores y volúmenes? (s/n):
set /p cleanup=""

if /i "%cleanup%"=="s" (
    echo.
    echo 🧹 Limpiando contenedores y volúmenes...
    docker system prune -f
    echo ✅ Limpieza completada
)

echo.
echo ✨ ¡Listo!
pause
