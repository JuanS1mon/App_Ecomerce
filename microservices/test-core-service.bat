@echo off
REM Script simplificado para iniciar solo el core-service primero

echo 🚀 Iniciando Core Service...
echo ================================

REM Cambiar al directorio del core-service
cd /d "C:\Users\PCJuan\Desktop\sql_app\microservices\core-service"

REM Verificar que Python está disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está disponible
    pause
    exit /b 1
)

REM Instalar dependencias
echo 📦 Instalando dependencias...
pip install -r requirements.txt

REM Iniciar el servicio
echo 🚀 Iniciando Core Service en puerto 8001...
python main.py

pause
