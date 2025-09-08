# ============================================================================
# CORE SERVICE - OPTIMIZADO CON ASYNC/AWAIT
# ============================================================================
# Versión optimizada con operaciones asíncronas concurrentes

import sys
import os
import asyncio
import aiohttp
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Dict, List, Optional
from pydantic import BaseModel
import time
from datetime import datetime

# =============================
# CONFIGURACIÓN DE LOGGING
# =============================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("core-service-optimized")

# =============================
# MODELOS OPTIMIZADOS
# =============================
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    modules: Dict[str, str]
    response_time_ms: float
    timestamp: str

class ServiceCommunication(BaseModel):
    service_name: str
    endpoint: str
    status: str
    response_time_ms: Optional[float] = None
    error: Optional[str] = None

# =============================
# CLIENTE HTTP ASYNC GLOBAL
# =============================
class AsyncHTTPClient:
    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None
    
    async def get_client(self) -> httpx.AsyncClient:
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(10.0),  # Timeout global de 10s
                limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
            )
        return self.client
    
    async def close(self):
        if self.client:
            await self.client.aclose()

http_client = AsyncHTTPClient()

# =============================
# SIMULACIÓN DE OPERACIONES ASYNC
# =============================
async def check_database_connection() -> Dict:
    """Simula verificación async de base de datos"""
    await asyncio.sleep(0.1)  # Simula latencia de DB
    return {
        "status": "connected",
        "response_time_ms": 100,
        "pool_status": "healthy"
    }

async def check_cache_status() -> Dict:
    """Simula verificación async de cache (Redis)"""
    await asyncio.sleep(0.05)  # Simula latencia de cache
    return {
        "status": "connected",
        "response_time_ms": 50,
        "memory_usage": "45%"
    }

async def check_external_services() -> List[Dict]:
    """Verifica servicios externos de forma concurrente"""
    services = [
        {"name": "mail_service", "url": "http://localhost:8001/mail/health"},
        {"name": "auth_service", "url": "http://localhost:8001/auth/health"},
        {"name": "admin_service", "url": "http://localhost:8001/admin/health"}
    ]
    
    async def check_service(service_info: Dict) -> Dict:
        try:
            client = await http_client.get_client()
            start_time = time.time()
            response = await client.get(service_info["url"], timeout=2.0)
            response_time = (time.time() - start_time) * 1000
            
            return {
                "name": service_info["name"],
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time_ms": round(response_time, 2),
                "url": service_info["url"]
            }
        except Exception as e:
            return {
                "name": service_info["name"],
                "status": "error",
                "error": str(e),
                "url": service_info["url"]
            }
    
    # Ejecutar verificaciones concurrentemente
    results = await asyncio.gather(*[
        check_service(service) for service in services
    ], return_exceptions=True)
    
    # Procesar resultados, manejando excepciones
    processed_results = []
    for result in results:
        if isinstance(result, Exception):
            processed_results.append({
                "name": "unknown",
                "status": "error",
                "error": str(result)
            })
        else:
            processed_results.append(result)
    
    return processed_results

# =============================
# OPERACIONES ASYNC OPTIMIZADAS
# =============================
async def get_system_metrics() -> Dict:
    """Obtiene métricas del sistema de forma concurrente"""
    start_time = time.time()
    
    # Ejecutar múltiples verificaciones en paralelo
    db_status, cache_status, services_status = await asyncio.gather(
        check_database_connection(),
        check_cache_status(),
        check_external_services(),
        return_exceptions=True
    )
    
    total_time = (time.time() - start_time) * 1000
    
    return {
        "database": db_status if not isinstance(db_status, Exception) else {"status": "error", "error": str(db_status)},
        "cache": cache_status if not isinstance(cache_status, Exception) else {"status": "error", "error": str(cache_status)},
        "external_services": services_status if not isinstance(services_status, Exception) else [],
        "total_check_time_ms": round(total_time, 2),
        "timestamp": datetime.now().isoformat()
    }

async def notify_service_events(event_type: str, event_data: Dict) -> None:
    """Notifica eventos a servicios externos de forma async"""
    notification_endpoints = [
        "http://localhost:8002/stock/notifications",
        "http://localhost:8003/obras/notifications",
        "http://localhost:8004/tickets/notifications"
    ]
    
    async def send_notification(endpoint: str) -> Dict:
        try:
            client = await http_client.get_client()
            response = await client.post(
                endpoint,
                json={"event_type": event_type, "data": event_data},
                timeout=3.0
            )
            return {
                "endpoint": endpoint,
                "status": "sent" if response.status_code < 300 else "failed",
                "status_code": response.status_code
            }
        except Exception as e:
            return {
                "endpoint": endpoint,
                "status": "error",
                "error": str(e)
            }
    
    # Enviar notificaciones concurrentemente (fire and forget)
    await asyncio.gather(*[
        send_notification(endpoint) for endpoint in notification_endpoints
    ], return_exceptions=True)

# =============================
# EVENTOS DE CICLO DE VIDA OPTIMIZADOS
# =============================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Iniciando Core Service Optimizado")
    logger.info("📋 Módulos activos: admin, security, mail, chat, mensajes")
    
    # Inicializar cliente HTTP async
    await http_client.get_client()
    
    # Verificación inicial concurrente
    startup_tasks = await asyncio.gather(
        check_database_connection(),
        check_cache_status(),
        return_exceptions=True
    )
    
    logger.info("✅ Verificaciones de startup completadas")
    
    yield
    
    # Shutdown
    logger.info("🛑 Cerrando Core Service Optimizado")
    await http_client.close()

# =============================
# INICIALIZACIÓN DE LA APP
# =============================
app = FastAPI(
    title="Core Service Optimized",
    description="Servicio principal optimizado con async/await",
    version="1.1.0",
    docs_url="/core/docs",
    redoc_url="/core/redoc",
    lifespan=lifespan
)

# =============================
# CONFIGURACIÓN DE CORS
# =============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# HEALTH CHECK OPTIMIZADO
# =============================
@app.get("/core/health", response_model=HealthResponse)
async def health_check():
    """Health check optimizado con verificaciones concurrentes"""
    start_time = time.time()
    
    # Verificaciones básicas concurrentes
    basic_checks = await asyncio.gather(
        check_database_connection(),
        check_cache_status(),
        return_exceptions=True
    )
    
    response_time_ms = (time.time() - start_time) * 1000
    
    return HealthResponse(
        status="healthy",
        service="core-service-optimized",
        version="1.1.0",
        modules={
            "admin": "active",
            "security": "active",
            "mail": "active",
            "chat": "active",
            "mensajes": "active"
        },
        response_time_ms=round(response_time_ms, 2),
        timestamp=datetime.now().isoformat()
    )

# =============================
# HEALTH CHECK COMPLETO
# =============================
@app.get("/core/health/detailed")
async def detailed_health_check():
    """Health check detallado con métricas completas"""
    metrics = await get_system_metrics()
    return {
        "status": "healthy",
        "service": "core-service-optimized",
        "version": "1.1.0",
        "metrics": metrics
    }

# =============================
# ENDPOINTS OPTIMIZADOS
# =============================
@app.get("/core/admin/users")
async def get_users_optimized(
    page: int = 1, 
    limit: int = 10,
    search: Optional[str] = None,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Endpoint optimizado para obtener usuarios con operaciones concurrentes"""
    start_time = time.time()
    
    # Simular múltiples operaciones de DB concurrentes
    users_task = asyncio.create_task(get_users_from_db(page, limit, search))
    count_task = asyncio.create_task(get_users_count(search))
    permissions_task = asyncio.create_task(get_user_permissions())
    
    # Ejecutar tareas concurrentemente
    users, total_count, permissions = await asyncio.gather(
        users_task,
        count_task, 
        permissions_task,
        return_exceptions=True
    )
    
    # Registrar evento en background
    background_tasks.add_task(
        notify_service_events,
        "user_list_accessed",
        {"page": page, "limit": limit, "search": search}
    )
    
    response_time = (time.time() - start_time) * 1000
    
    return {
        "users": users if not isinstance(users, Exception) else [],
        "total": total_count if not isinstance(total_count, Exception) else 0,
        "permissions": permissions if not isinstance(permissions, Exception) else {},
        "page": page,
        "limit": limit,
        "response_time_ms": round(response_time, 2)
    }

# =============================
# OPERACIONES SIMULADAS ASYNC
# =============================
async def get_users_from_db(page: int, limit: int, search: Optional[str]) -> List[Dict]:
    """Simula obtención async de usuarios de DB"""
    await asyncio.sleep(0.1)  # Simula latencia de DB
    
    # Datos demo
    users = [
        {"id": i, "name": f"Usuario {i}", "email": f"user{i}@example.com"}
        for i in range((page-1)*limit + 1, page*limit + 1)
    ]
    
    if search:
        users = [u for u in users if search.lower() in u["name"].lower()]
    
    return users

async def get_users_count(search: Optional[str]) -> int:
    """Simula conteo async de usuarios"""
    await asyncio.sleep(0.05)  # Simula query de conteo
    return 150 if not search else 25

async def get_user_permissions() -> Dict:
    """Simula obtención async de permisos"""
    await asyncio.sleep(0.03)  # Simula consulta de permisos
    return {
        "can_create": True,
        "can_edit": True,
        "can_delete": False,
        "admin_level": 2
    }

# =============================
# COMUNICACIÓN ENTRE SERVICIOS
# =============================
@app.get("/core/services/status")
async def get_all_services_status():
    """Obtiene status de todos los microservicios concurrentemente"""
    microservices = [
        {"name": "stock", "url": "http://localhost:8002/stock/health"},
        {"name": "obras", "url": "http://localhost:8003/obras/health"},
        {"name": "tickets", "url": "http://localhost:8004/tickets/health"}
    ]
    
    async def check_microservice(service: Dict) -> ServiceCommunication:
        try:
            client = await http_client.get_client()
            start_time = time.time()
            response = await client.get(service["url"], timeout=3.0)
            response_time = (time.time() - start_time) * 1000
            
            return ServiceCommunication(
                service_name=service["name"],
                endpoint=service["url"],
                status="healthy" if response.status_code == 200 else "unhealthy",
                response_time_ms=round(response_time, 2)
            )
        except Exception as e:
            return ServiceCommunication(
                service_name=service["name"],
                endpoint=service["url"],
                status="error",
                error=str(e)
            )
    
    # Verificar todos los servicios concurrentemente
    services_status = await asyncio.gather(*[
        check_microservice(service) for service in microservices
    ], return_exceptions=True)
    
    return {
        "services": [
            status.dict() if not isinstance(status, Exception) else {
                "service_name": "unknown",
                "status": "error",
                "error": str(status)
            }
            for status in services_status
        ],
        "total_services": len(microservices),
        "timestamp": datetime.now().isoformat()
    }

# =============================
# PÁGINA PRINCIPAL
# =============================
@app.get("/")
async def root():
    """Página principal optimizada"""
    # Obtener info básica de forma rápida
    system_info = await asyncio.create_task(
        asyncio.wait_for(get_system_metrics(), timeout=5.0)
    )
    
    return {
        "message": "Core Service Optimizado - API Principal",
        "version": "1.1.0",
        "docs": "/core/docs",
        "health": "/core/health",
        "detailed_health": "/core/health/detailed",
        "services_status": "/core/services/status",
        "optimizations": [
            "Async/await implementation",
            "Concurrent operations",
            "HTTP client pooling",
            "Background tasks",
            "Timeout handling"
        ],
        "performance": {
            "last_health_check_ms": system_info.get("total_check_time_ms", 0)
        }
    }

# =============================
# MANEJADOR DE ERRORES OPTIMIZADO
# =============================
@app.exception_handler(Exception)
async def optimized_exception_handler(request: Request, exc: Exception):
    """Manejador de errores con logging async"""
    
    # Log async en background
    asyncio.create_task(log_error_async(request, exc))
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error in core service",
            "detail": str(exc),
            "service": "core-service-optimized",
            "timestamp": datetime.now().isoformat()
        }
    )

async def log_error_async(request: Request, exc: Exception):
    """Log de errores de forma asíncrona"""
    await asyncio.sleep(0.01)  # Simula operación async de logging
    logger.error(f"Error en Core Service Optimizado: {str(exc)} - URL: {request.url}")

# =============================
# EJECUCIÓN OPTIMIZADA
# =============================
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando Core Service Optimizado en puerto 8001")
    
    # Configuración optimizada de uvicorn (Windows compatible)
    uvicorn.run(
        "main_optimized:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        workers=1,  # Para desarrollo, en producción usar más workers
        # loop="uvloop",  # No disponible en Windows
        # http="httptools",  # No siempre disponible en Windows
        access_log=False,  # Deshabilitar para mejor performance
        log_level="info"
    )
