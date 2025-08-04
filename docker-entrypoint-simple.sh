#!/bin/bash
# ==========================================
# SCRIPT DE ENTRADA SIMPLIFICADO 
# ==========================================

set -e

echo "🚀 Iniciando aplicación FastAPI (desarrollo)..."
echo "📅 Fecha: $(date)"
echo "🌍 Entorno: ${ENVIRONMENT:-development}"

# Esperar un momento para que todo esté listo
echo "⏳ Preparando entorno..."
sleep 2

echo "🎉 Inicialización completada!"
echo "🚀 Iniciando servidor FastAPI..."

# Ejecutar el comando pasado como argumentos
exec "$@"
