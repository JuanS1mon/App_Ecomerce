#!/bin/bash

# ============================================================================
# SCRIPT DE INICIO PARA MICROSERVICIOS
# ============================================================================
# Este script inicia todos los servicios de la arquitectura de microservicios

echo "🚀 Iniciando arquitectura de microservicios..."
echo "================================================"

# Verificar que Docker y Docker Compose estén instalados
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

# Cambiar al directorio de microservicios
cd "$(dirname "$0")"

# Crear directorios necesarios
echo "📁 Creando directorios necesarios..."
mkdir -p logs/core logs/stock logs/obras logs/nginx
mkdir -p static/core static/stock static/obras
mkdir -p monitoring

# Construir e iniciar los servicios
echo "🏗️ Construyendo e iniciando servicios..."
docker-compose -f docker-compose.microservices.yml up --build -d

# Verificar el estado de los servicios
echo "⏳ Esperando que los servicios estén listos..."
sleep 30

echo "🔍 Verificando estado de los servicios..."
echo "================================================"

# Health checks
echo "Core Service:"
curl -s http://localhost:8001/core/health | jq '.' || echo "❌ Core Service no responde"

echo -e "\nStock Service:"
curl -s http://localhost:8002/stock/health | jq '.' || echo "❌ Stock Service no responde"

echo -e "\nObras Service:"
curl -s http://localhost:8003/obras/health | jq '.' || echo "❌ Obras Service no responde"

echo -e "\nAPI Gateway:"
curl -s http://localhost/health || echo "❌ API Gateway no responde"

echo -e "\n================================================"
echo "✅ Servicios iniciados correctamente!"
echo ""
echo "🔗 URLs disponibles:"
echo "   • API Gateway: http://localhost"
echo "   • Core Service: http://localhost:8001/core/docs"
echo "   • Stock Service: http://localhost:8002/stock/docs"
echo "   • Obras Service: http://localhost:8003/obras/docs"
echo "   • Monitoring (Grafana): http://localhost:3000"
echo "   • Metrics (Prometheus): http://localhost:9090"
echo ""
echo "📋 Para ver logs: docker-compose -f docker-compose.microservices.yml logs -f [servicio]"
echo "🛑 Para detener: ./stop-microservices.sh"
