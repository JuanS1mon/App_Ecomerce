# ============================================================================
# STOCK SERVICE - OPTIMIZADO CON ASYNC/AWAIT
# ============================================================================
# Versión optimizada con operaciones asíncronas concurrentes

import sys
import os
import asyncio
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Dict, List, Optional, Union
from pydantic import BaseModel
import time
from datetime import datetime
import json

# =============================
# CONFIGURACIÓN DE LOGGING
# =============================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("stock-service-optimized")

# =============================
# MODELOS OPTIMIZADOS
# =============================
class Article(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category: Optional[str] = None
    supplier: Optional[str] = None
    
class StockMovement(BaseModel):
    id: Optional[int] = None
    article_id: int
    movement_type: str  # 'entrada', 'salida', 'ajuste'
    quantity: int
    reason: Optional[str] = None
    timestamp: Optional[str] = None

class InventoryReport(BaseModel):
    total_articles: int
    total_stock_value: float
    low_stock_items: List[Dict]
    top_articles: List[Dict]
    recent_movements: List[Dict]
    generation_time_ms: float

# =============================
# CLIENTE HTTP ASYNC
# =============================
class AsyncHTTPClient:
    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None
    
    async def get_client(self) -> httpx.AsyncClient:
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(10.0),
                limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
            )
        return self.client
    
    async def close(self):
        if self.client:
            await self.client.aclose()

http_client = AsyncHTTPClient()

# =============================
# BASE DE DATOS SIMULADA (ASYNC)
# =============================
# En producción, usar SQLAlchemy async o similar
class AsyncStockDatabase:
    def __init__(self):
        self.articles = [
            {"id": 1, "name": "Laptop HP", "price": 899.99, "stock": 15, "category": "Electronics", "supplier": "HP Inc"},
            {"id": 2, "name": "Mouse Logitech", "price": 29.99, "stock": 45, "category": "Accessories", "supplier": "Logitech"},
            {"id": 3, "name": "Teclado Mecánico", "price": 79.99, "stock": 8, "category": "Accessories", "supplier": "Corsair"},
            {"id": 4, "name": "Monitor 24\"", "price": 199.99, "stock": 12, "category": "Electronics", "supplier": "Samsung"},
            {"id": 5, "name": "Cables USB-C", "price": 15.99, "stock": 2, "category": "Cables", "supplier": "Anker"}
        ]
        
        self.movements = [
            {"id": 1, "article_id": 1, "movement_type": "entrada", "quantity": 5, "reason": "Compra", "timestamp": "2025-08-20T10:00:00"},
            {"id": 2, "article_id": 2, "movement_type": "salida", "quantity": 3, "reason": "Venta", "timestamp": "2025-08-21T14:30:00"},
            {"id": 3, "article_id": 3, "movement_type": "ajuste", "quantity": -2, "reason": "Inventario", "timestamp": "2025-08-22T09:15:00"}
        ]
    
    async def get_articles(self, page: int = 1, limit: int = 10, category: Optional[str] = None) -> List[Dict]:
        """Simula query async de artículos"""
        await asyncio.sleep(0.05)  # Simula latencia de DB
        
        articles = self.articles.copy()
        if category:
            articles = [a for a in articles if a["category"] == category]
        
        start = (page - 1) * limit
        end = start + limit
        return articles[start:end]
    
    async def get_article_by_id(self, article_id: int) -> Optional[Dict]:
        """Simula query async de artículo específico"""
        await asyncio.sleep(0.03)
        return next((a for a in self.articles if a["id"] == article_id), None)
    
    async def get_low_stock_items(self, threshold: int = 10) -> List[Dict]:
        """Simula query async de items con bajo stock"""
        await asyncio.sleep(0.08)
        return [a for a in self.articles if a["stock"] <= threshold]
    
    async def get_total_stock_value(self) -> float:
        """Calcula valor total del stock de forma async"""
        await asyncio.sleep(0.1)
        return sum(a["price"] * a["stock"] for a in self.articles)
    
    async def get_recent_movements(self, limit: int = 10) -> List[Dict]:
        """Obtiene movimientos recientes"""
        await asyncio.sleep(0.06)
        return sorted(self.movements, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    async def add_article(self, article_data: Dict) -> Dict:
        """Simula inserción async de artículo"""
        await asyncio.sleep(0.07)
        new_id = max([a["id"] for a in self.articles]) + 1
        new_article = {**article_data, "id": new_id}
        self.articles.append(new_article)
        return new_article
    
    async def update_stock(self, article_id: int, new_stock: int) -> bool:
        """Actualiza stock de forma async"""
        await asyncio.sleep(0.04)
        article = next((a for a in self.articles if a["id"] == article_id), None)
        if article:
            article["stock"] = new_stock
            return True
        return False

# Instancia global de la base de datos
db = AsyncStockDatabase()

# =============================
# OPERACIONES ASYNC OPTIMIZADAS
# =============================
async def calculate_stock_metrics() -> Dict:
    """Calcula métricas de stock de forma concurrente"""
    start_time = time.time()
    
    # Ejecutar múltiples cálculos concurrentemente
    total_value_task = asyncio.create_task(db.get_total_stock_value())
    low_stock_task = asyncio.create_task(db.get_low_stock_items())
    recent_movements_task = asyncio.create_task(db.get_recent_movements())
    articles_task = asyncio.create_task(db.get_articles(limit=5))
    
    # Esperar a que todas las tareas terminen
    total_value, low_stock, recent_movements, top_articles = await asyncio.gather(
        total_value_task,
        low_stock_task,
        recent_movements_task,
        articles_task,
        return_exceptions=True
    )
    
    calculation_time = (time.time() - start_time) * 1000
    
    return {
        "total_stock_value": total_value if not isinstance(total_value, Exception) else 0,
        "low_stock_items": low_stock if not isinstance(low_stock, Exception) else [],
        "recent_movements": recent_movements if not isinstance(recent_movements, Exception) else [],
        "top_articles": top_articles if not isinstance(top_articles, Exception) else [],
        "calculation_time_ms": round(calculation_time, 2),
        "timestamp": datetime.now().isoformat()
    }

async def notify_stock_change(article_id: int, old_stock: int, new_stock: int) -> None:
    """Notifica cambios de stock a otros servicios"""
    notification_data = {
        "article_id": article_id,
        "old_stock": old_stock,
        "new_stock": new_stock,
        "change": new_stock - old_stock,
        "timestamp": datetime.now().isoformat()
    }
    
    # Endpoints de notificación
    endpoints = [
        "http://localhost:8001/core/notifications",
        "http://localhost:8003/obras/stock-updates",
        "http://localhost:8004/tickets/stock-alerts"
    ]
    
    async def send_notification(endpoint: str) -> Dict:
        try:
            client = await http_client.get_client()
            response = await client.post(
                endpoint,
                json=notification_data,
                timeout=3.0
            )
            return {"endpoint": endpoint, "status": "sent", "status_code": response.status_code}
        except Exception as e:
            return {"endpoint": endpoint, "status": "error", "error": str(e)}
    
    # Enviar notificaciones concurrentemente
    await asyncio.gather(*[
        send_notification(endpoint) for endpoint in endpoints
    ], return_exceptions=True)

async def sync_with_external_systems(article_data: Dict) -> Dict:
    """Sincroniza con sistemas externos de forma async"""
    external_apis = [
        {"name": "supplier_api", "url": "https://api.supplier.com/stock"},
        {"name": "accounting_api", "url": "https://api.accounting.com/inventory"},
        {"name": "warehouse_api", "url": "https://api.warehouse.com/update"}
    ]
    
    async def sync_with_api(api_info: Dict) -> Dict:
        try:
            # Simular llamada a API externa
            await asyncio.sleep(0.2)  # Simula latencia de API externa
            return {
                "api": api_info["name"],
                "status": "synced",
                "response_time_ms": 200
            }
        except Exception as e:
            return {
                "api": api_info["name"],
                "status": "error",
                "error": str(e)
            }
    
    # Sincronizar con todas las APIs concurrentemente
    sync_results = await asyncio.gather(*[
        sync_with_api(api) for api in external_apis
    ], return_exceptions=True)
    
    return {
        "sync_results": [
            result if not isinstance(result, Exception) else {
                "api": "unknown",
                "status": "error",
                "error": str(result)
            }
            for result in sync_results
        ]
    }

# =============================
# EVENTOS DE CICLO DE VIDA
# =============================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Iniciando Stock Service Optimizado")
    logger.info("📦 Módulos activos: inventory, articles, stock calculation")
    
    # Inicializar recursos async
    await http_client.get_client()
    
    # Verificaciones iniciales concurrentes
    startup_checks = await asyncio.gather(
        db.get_articles(limit=1),
        calculate_stock_metrics(),
        return_exceptions=True
    )
    
    logger.info("✅ Verificaciones de startup completadas")
    
    yield
    
    # Shutdown
    logger.info("🛑 Cerrando Stock Service Optimizado")
    await http_client.close()

# =============================
# INICIALIZACIÓN DE LA APP
# =============================
app = FastAPI(
    title="Stock Service Optimized",
    description="Servicio de stock optimizado con async/await",
    version="1.1.0",
    docs_url="/stock/docs",
    redoc_url="/stock/redoc",
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
@app.get("/stock/health")
async def health_check():
    """Health check optimizado con verificaciones concurrentes"""
    start_time = time.time()
    
    # Verificaciones concurrentes
    db_check = asyncio.create_task(db.get_articles(limit=1))
    metrics_check = asyncio.create_task(calculate_stock_metrics())
    
    try:
        # Ejecutar verificaciones con timeout
        await asyncio.wait_for(asyncio.gather(db_check, metrics_check), timeout=5.0)
        status = "healthy"
    except asyncio.TimeoutError:
        status = "degraded"
    except Exception:
        status = "unhealthy"
    
    response_time = (time.time() - start_time) * 1000
    
    return {
        "status": status,
        "service": "stock-service-optimized",
        "version": "1.1.0",
        "features": {
            "inventory_management": "active",
            "stock_calculation": "active",
            "articles_crud": "active",
            "real_time_updates": "active",
            "async_operations": "active"
        },
        "response_time_ms": round(response_time, 2),
        "timestamp": datetime.now().isoformat()
    }

# =============================
# ENDPOINTS OPTIMIZADOS
# =============================
@app.get("/stock/articles")
async def get_articles_optimized(
    page: int = 1,
    limit: int = 10,
    category: Optional[str] = None,
    include_metrics: bool = False
):
    """Endpoint optimizado para obtener artículos"""
    start_time = time.time()
    
    # Operación principal
    articles_task = asyncio.create_task(db.get_articles(page, limit, category))
    
    # Operaciones opcionales concurrentes
    tasks = [articles_task]
    if include_metrics:
        metrics_task = asyncio.create_task(calculate_stock_metrics())
        tasks.append(metrics_task)
    
    # Ejecutar tareas concurrentemente
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    articles = results[0] if not isinstance(results[0], Exception) else []
    metrics = results[1] if len(results) > 1 and not isinstance(results[1], Exception) else None
    
    response_time = (time.time() - start_time) * 1000
    
    response = {
        "articles": articles,
        "page": page,
        "limit": limit,
        "category": category,
        "response_time_ms": round(response_time, 2)
    }
    
    if metrics:
        response["metrics"] = metrics
    
    return response

@app.get("/stock/articles/{article_id}")
async def get_article_optimized(article_id: int):
    """Obtiene artículo específico con información relacionada"""
    start_time = time.time()
    
    # Obtener información concurrentemente
    article_task = asyncio.create_task(db.get_article_by_id(article_id))
    movements_task = asyncio.create_task(db.get_recent_movements())
    
    article, movements = await asyncio.gather(
        article_task,
        movements_task,
        return_exceptions=True
    )
    
    if isinstance(article, Exception) or not article:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    
    # Filtrar movimientos del artículo
    article_movements = [
        m for m in (movements if not isinstance(movements, Exception) else [])
        if m["article_id"] == article_id
    ]
    
    response_time = (time.time() - start_time) * 1000
    
    return {
        "article": article,
        "recent_movements": article_movements,
        "response_time_ms": round(response_time, 2)
    }

@app.post("/stock/articles")
async def create_article_optimized(
    article: Article,
    background_tasks: BackgroundTasks
):
    """Crea artículo nuevo con operaciones async"""
    start_time = time.time()
    
    # Crear artículo
    new_article = await db.add_article(article.dict(exclude={"id"}))
    
    # Operaciones en background
    background_tasks.add_task(
        sync_with_external_systems,
        new_article
    )
    
    background_tasks.add_task(
        notify_stock_change,
        new_article["id"],
        0,
        new_article["stock"]
    )
    
    response_time = (time.time() - start_time) * 1000
    
    return {
        "article": new_article,
        "message": "Artículo creado exitosamente",
        "response_time_ms": round(response_time, 2),
        "background_tasks": ["external_sync", "stock_notification"]
    }

@app.put("/stock/articles/{article_id}/stock")
async def update_stock_optimized(
    article_id: int,
    new_stock: int,
    background_tasks: BackgroundTasks
):
    """Actualiza stock con notificaciones async"""
    start_time = time.time()
    
    # Obtener stock actual
    article = await db.get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    
    old_stock = article["stock"]
    
    # Actualizar stock
    success = await db.update_stock(article_id, new_stock)
    
    if success:
        # Notificaciones en background
        background_tasks.add_task(
            notify_stock_change,
            article_id,
            old_stock,
            new_stock
        )
    
    response_time = (time.time() - start_time) * 1000
    
    return {
        "success": success,
        "article_id": article_id,
        "old_stock": old_stock,
        "new_stock": new_stock,
        "change": new_stock - old_stock,
        "response_time_ms": round(response_time, 2)
    }

@app.get("/stock/inventory/report", response_model=InventoryReport)
async def get_inventory_report_optimized():
    """Genera reporte completo de inventario de forma optimizada"""
    start_time = time.time()
    
    # Ejecutar múltiples consultas concurrentemente
    metrics_task = asyncio.create_task(calculate_stock_metrics())
    articles_count_task = asyncio.create_task(db.get_articles(limit=1000))  # Para contar
    
    metrics, all_articles = await asyncio.gather(
        metrics_task,
        articles_count_task,
        return_exceptions=True
    )
    
    if isinstance(metrics, Exception):
        metrics = {}
    if isinstance(all_articles, Exception):
        all_articles = []
    
    generation_time = (time.time() - start_time) * 1000
    
    return InventoryReport(
        total_articles=len(all_articles),
        total_stock_value=metrics.get("total_stock_value", 0),
        low_stock_items=metrics.get("low_stock_items", []),
        top_articles=metrics.get("top_articles", []),
        recent_movements=metrics.get("recent_movements", []),
        generation_time_ms=round(generation_time, 2)
    )

# =============================
# PÁGINA PRINCIPAL
# =============================
@app.get("/")
async def root():
    """Página principal optimizada"""
    # Info rápida del servicio
    quick_metrics = await asyncio.create_task(
        asyncio.wait_for(calculate_stock_metrics(), timeout=2.0)
    )
    
    return {
        "message": "Stock Service Optimizado - Gestión de Inventario",
        "version": "1.1.0",
        "docs": "/stock/docs",
        "health": "/stock/health",
        "optimizations": [
            "Async database operations",
            "Concurrent API calls",
            "Background task processing",
            "External system sync",
            "Real-time notifications"
        ],
        "quick_metrics": {
            "total_stock_value": quick_metrics.get("total_stock_value", 0),
            "low_stock_items": len(quick_metrics.get("low_stock_items", [])),
            "last_calculation_ms": quick_metrics.get("calculation_time_ms", 0)
        }
    }

# =============================
# MANEJADOR DE ERRORES
# =============================
@app.exception_handler(Exception)
async def optimized_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error en Stock Service Optimizado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error in stock service",
            "detail": str(exc),
            "service": "stock-service-optimized",
            "timestamp": datetime.now().isoformat()
        }
    )

# =============================
# EJECUCIÓN OPTIMIZADA
# =============================
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando Stock Service Optimizado en puerto 8002")
    
    uvicorn.run(
        "main_optimized:app",
        host="0.0.0.0",
        port=8002,
        reload=False,
        workers=1,
        # loop="uvloop",  # No disponible en Windows
        # http="httptools",  # No siempre disponible en Windows
        access_log=False,
        log_level="info"
    )
