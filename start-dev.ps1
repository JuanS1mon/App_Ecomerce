#!/usr/bin/env powershell
# ============================================================================
# START-DEV.PS1 - SCRIPT DE INICIO PARA DESARROLLO
# ============================================================================
# Script para iniciar el servidor de desarrollo del Sistema de Stock
# Incluye verificaciones y configuración automática

Write-Host "🚀 SISTEMA DE STOCK - SERVIDOR DE DESARROLLO" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar directorio actual
$currentDir = Get-Location
Write-Host "📁 Directorio actual: $currentDir" -ForegroundColor Yellow

if (-not (Test-Path "main_simple.py")) {
    Write-Host "❌ Error: No se encontró main_simple.py" -ForegroundColor Red
    Write-Host "   Asegúrate de estar en el directorio del proyecto" -ForegroundColor Red
    exit 1
}

# Verificar si el entorno virtual está activado
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if ($pythonPath -like "*env*Scripts*") {
    Write-Host "✅ Entorno virtual activado: $pythonPath" -ForegroundColor Green
} else {
    Write-Host "⚠️  Activando entorno virtual..." -ForegroundColor Yellow
    try {
        & "sql_app\env\Scripts\Activate.ps1"
        Write-Host "✅ Entorno virtual activado" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error al activar entorno virtual" -ForegroundColor Red
        Write-Host "   Ejecuta manualmente: & sql_app\env\Scripts\Activate.ps1" -ForegroundColor Red
        exit 1
    }
}

# Verificar puerto libre
$portCheck = netstat -ano | Select-String ":8001"
if ($portCheck) {
    Write-Host "⚠️  Puerto 8001 puede estar ocupado:" -ForegroundColor Yellow
    Write-Host "$portCheck" -ForegroundColor Gray
    $response = Read-Host "¿Continuar de todos modos? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "❌ Operación cancelada" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🎯 INICIANDO SERVIDOR DE DESARROLLO" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host "📊 Configuración:" -ForegroundColor White
Write-Host "   • Host: 127.0.0.1" -ForegroundColor Gray
Write-Host "   • Puerto: 8001" -ForegroundColor Gray
Write-Host "   • Aplicación: main_simple:app" -ForegroundColor Gray
Write-Host "   • Reload: Activado" -ForegroundColor Gray
Write-Host "   • Log Level: info" -ForegroundColor Gray
Write-Host ""
Write-Host "🌐 URLs disponibles:" -ForegroundColor White
Write-Host "   • Principal: http://localhost:8001/" -ForegroundColor Cyan
Write-Host "   • Editor Visual: http://localhost:8001/editor-visual" -ForegroundColor Cyan
Write-Host "   • Generador: http://localhost:8001/generar/test" -ForegroundColor Cyan
Write-Host ""
Write-Host "🛑 Para detener el servidor presiona Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Comando principal
uvicorn main_simple:app --host 127.0.0.1 --port 8001 --reload --log-level info