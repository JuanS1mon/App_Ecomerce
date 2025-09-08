@echo off
REM ============================================================================
REM SCRIPT DE PARADA PARA MICROSERVICIOS (WINDOWS)
REM ============================================================================

echo 🛑 Deteniendo arquitectura de microservicios...
echo ================================================

REM Detener y eliminar contenedores
docker-compose -f docker-compose.microservices.yml down

echo ✅ Servicios detenidos correctamente!
echo.
echo 🗑️ Para limpiar completamente (eliminar volúmenes):
echo    docker-compose -f docker-compose.microservices.yml down -v
echo.
echo 🧹 Para eliminar imágenes no utilizadas:
echo    docker system prune -f
echo.
pause
