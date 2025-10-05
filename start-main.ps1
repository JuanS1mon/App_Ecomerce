#!/usr/bin/env powershell
# ============================================================================
# START-MAIN.PS1 - SCRIPT DE INICIO PARA SERVIDOR PRINCIPAL
# ============================================================================
# Script para iniciar el servidor principal con todas las funcionalidades
# Incluye verificaciones de migraciones y configuración completa

Write-Host "🚀 SISTEMA DE STOCK - SERVIDOR PRINCIPAL" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar directorio actual
$currentDir = Get-Location
Write-Host "📁 Directorio actual: $currentDir" -ForegroundColor Yellow

if (-not (Test-Path "main.py")) {
    Write-Host "❌ Error: No se encontró main.py" -ForegroundColor Red
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
$portCheck = netstat -ano | Select-String ":8000"
if ($portCheck) {
    Write-Host "⚠️  Puerto 8000 puede estar ocupado:" -ForegroundColor Yellow
    Write-Host "$portCheck" -ForegroundColor Gray
    $response = Read-Host "¿Continuar de todos modos? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "❌ Operación cancelada" -ForegroundColor Red
        exit 1
    }
}

# Verificar estado de Alembic
Write-Host "🔍 Verificando estado de migraciones..." -ForegroundColor Yellow
try {
    $alembicCheck = alembic current 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migraciones OK" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Advertencia: Posibles problemas con migraciones" -ForegroundColor Yellow
        Write-Host "   Si hay errores, usa start-dev.ps1 en su lugar" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  No se pudo verificar Alembic" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 INICIANDO SERVIDOR PRINCIPAL" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green
Write-Host "📊 Configuración:" -ForegroundColor White
Write-Host "   • Host: 127.0.0.1" -ForegroundColor Gray
Write-Host "   • Puerto: 8000" -ForegroundColor Gray
Write-Host "   • Aplicación: main:app" -ForegroundColor Gray
Write-Host "   • Reload: Activado" -ForegroundColor Gray
Write-Host "   • Log Level: info" -ForegroundColor Gray
Write-Host ""
Write-Host "🌐 URLs disponibles:" -ForegroundColor White
Write-Host "   • Principal: http://localhost:8000/" -ForegroundColor Cyan
Write-Host "   • Admin: http://localhost:8000/admin" -ForegroundColor Cyan
Write-Host "   • API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   • Editor Visual: http://localhost:8000/editor-visual" -ForegroundColor Cyan
Write-Host "   • Generador: http://localhost:8000/generar/" -ForegroundColor Cyan
Write-Host ""
Write-Host "🛑 Para detener el servidor presiona Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Comando principal
uvicorn main:app --host 127.0.0.1 --port 8000 --reload --log-level info