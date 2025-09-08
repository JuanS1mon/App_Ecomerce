#!/bin/bash
# Script para iniciar todos los microservicios

echo "======================================"
echo "  INICIANDO MICROSERVICIOS INDIVIDUALES"
echo "======================================"

echo ""
echo "[1/5] Iniciando Core Service (Puerto 8001)..."
cd microservices/core-service
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
cd ../..
sleep 3

echo "[2/5] Iniciando Stock Service (Puerto 8002)..."
cd microservices/stock-service
python -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload &
cd ../..
sleep 3

echo "[3/5] Iniciando Obras Service (Puerto 8003)..."
cd microservices/obras-service
python -m uvicorn main:app --host 0.0.0.0 --port 8003 --reload &
cd ../..
sleep 3

echo "[4/5] Iniciando Tickets Service (Puerto 8004)..."
cd microservices/tickets-service
python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload &
cd ../..
sleep 3

echo "[5/5] Esperando que los servicios estén listos..."
sleep 10

echo ""
echo "✅ TODOS LOS SERVICIOS INICIADOS"
echo ""
echo "📊 URLs de los Servicios:"
echo "   Core Service:    http://localhost:8001/core/docs"
echo "   Stock Service:   http://localhost:8002/stock/docs"
echo "   Obras Service:   http://localhost:8003/obras/docs"
echo "   Tickets Service: http://localhost:8004/tickets/docs"
echo ""
echo "📋 Dashboard: file://$(pwd)/microservices/dashboard.html"
echo ""
echo "Presiona Ctrl+C para detener todos los servicios..."

# Mantener el script ejecutándose
wait