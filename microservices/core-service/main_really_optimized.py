#!/usr/bin/env python3
"""
CORE SERVICE VERDADERAMENTE OPTIMIZADO
Aplicando async/await solo donde realmente mejora el rendimiento
"""

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import httpx
import uvicorn
import logging
import time
from typing import Dict, List
import os

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("core-service-real-optimized")

app = FastAPI(
    title="Core Service - Realmente Optimizado",
    description="Aplicando async/await solo donde realmente mejora el rendimiento",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Client HTTP reutilizable - solo se crea uno
http_client = None

@app.on_event("startup")
async def startup_event():
    """Inicialización eficiente - solo lo necesario"""
    global http_client
    logger.info("🚀 Iniciando Core Service Realmente Optimizado")
    
    # Cliente HTTP con pooling pero sin verificaciones innecesarias
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(5.0),
        limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
    )
    
    logger.info("✅ Core Service listo - Inicialización mínima")

@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza de recursos"""
    global http_client
    if http_client:
        await http_client.aclose()
    logger.info("🛑 Core Service cerrado")

# ENDPOINT SIMPLE - SIN async/await innecesario
@app.get("/core/health")
def health_simple():
    """
    Endpoint de salud SIMPLE y RÁPIDO
    NO usa async porque no lo necesita
    """
    return {
        "status": "healthy",
        "service": "core-service-real-optimized",
        "version": "2.0.0",
        "timestamp": time.time()
    }

# ENDPOINT QUE SÍ SE BENEFICIA de async/await
@app.get("/core/health/full")
async def health_with_checks():
    """
    Solo aquí usamos async porque realmente verificamos servicios externos
    """
    start_time = time.time()
    
    # Lista de servicios a verificar
    services_to_check = [
        ("stock", "http://localhost:8002/stock/health"),
        ("obras", "http://localhost:8003/obras/health"),
    ]
    
    async def check_service(name: str, url: str):
        try:
            response = await http_client.get(url, timeout=2.0)
            return {
                "name": name,
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time_ms": round((time.time() - start_time) * 1000, 1)
            }
        except Exception:
            return {
                "name": name,
                "status": "unreachable",
                "response_time_ms": None
            }
    
    # AQUÍ SÍ se beneficia de async - verificaciones concurrentes
    service_checks = await asyncio.gather(
        *[check_service(name, url) for name, url in services_to_check],
        return_exceptions=True
    )
    
    total_time = round((time.time() - start_time) * 1000, 1)
    
    return {
        "status": "healthy",
        "service": "core-service-real-optimized",
        "version": "2.0.0",
        "total_check_time_ms": total_time,
        "services": [check for check in service_checks if not isinstance(check, Exception)]
    }

# ENDPOINT para operaciones que SÍ necesitan async
@app.get("/core/services/status")
async def services_status():
    """
    Obtiene estado de múltiples servicios - AQUÍ async/await es útil
    """
    async def get_service_info(service_name: str, port: int):
        try:
            url = f"http://localhost:{port}/health"
            start = time.time()
            response = await http_client.get(url, timeout=3.0)
            response_time = round((time.time() - start) * 1000, 1)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "service": service_name,
                    "port": port,
                    "status": "online",
                    "response_time_ms": response_time,
                    "details": data
                }
        except Exception as e:
            return {
                "service": service_name,
                "port": port,
                "status": "offline",
                "error": str(e)
            }
    
    # Verificar servicios concurrentemente - AQUÍ async es beneficioso
    services = await asyncio.gather(
        get_service_info("main", 8000),
        get_service_info("stock", 8002), 
        get_service_info("obras", 8003),
        get_service_info("tickets", 8004),
        return_exceptions=True
    )
    
    return {
        "timestamp": time.time(),
        "services": [s for s in services if not isinstance(s, Exception)]
    }

# ENDPOINT para procesamiento en background - async útil
@app.post("/core/process/background")
async def process_in_background(background_tasks: BackgroundTasks):
    """
    Procesa algo en background - buen uso de async
    """
    
    async def heavy_process():
        logger.info("🔄 Iniciando proceso pesado en background")
        await asyncio.sleep(2)  # Simula trabajo pesado
        logger.info("✅ Proceso pesado completado")
    
    # Ejecutar en background sin bloquear la respuesta
    background_tasks.add_task(heavy_process)
    
    return {
        "message": "Proceso iniciado en background",
        "timestamp": time.time()
    }

# ENDPOINT para múltiples operaciones - async beneficioso
@app.get("/core/data/aggregated")
async def get_aggregated_data():
    """
    Obtiene datos de múltiples fuentes - buen caso para async
    """
    
    async def get_stock_data():
        try:
            response = await http_client.get("http://localhost:8002/stock/articles", timeout=5.0)
            return response.json() if response.status_code == 200 else []
        except:
            return []
    
    async def get_obras_data():
        try:
            response = await http_client.get("http://localhost:8003/obras/dashboard", timeout=5.0)
            return response.json() if response.status_code == 200 else {}
        except:
            return {}
    
    async def get_system_stats():
        # Simula obtener estadísticas del sistema
        await asyncio.sleep(0.1)
        return {
            "cpu_usage": "15%",
            "memory_usage": "45%",
            "disk_usage": "60%"
        }
    
    # Obtener todo concurrentemente - AQUÍ async es muy útil
    start_time = time.time()
    
    stock_data, obras_data, system_stats = await asyncio.gather(
        get_stock_data(),
        get_obras_data(), 
        get_system_stats(),
        return_exceptions=True
    )
    
    total_time = round((time.time() - start_time) * 1000, 1)
    
    return {
        "aggregation_time_ms": total_time,
        "data": {
            "stock": stock_data if not isinstance(stock_data, Exception) else [],
            "obras": obras_data if not isinstance(obras_data, Exception) else {},
            "system": system_stats if not isinstance(system_stats, Exception) else {}
        }
    }

if __name__ == "__main__":
    logger.info("🚀 Iniciando Core Service Realmente Optimizado en puerto 8005")
    
    # Configuración optimizada para Windows
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8005,
        log_level="info",
        access_log=False,  # Menos overhead
        # Sin uvloop en Windows - pero mantenemos las optimizaciones que sí funcionan
    )
