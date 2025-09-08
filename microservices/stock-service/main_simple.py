# ============================================================================
# STOCK SERVICE - MAIN APPLICATION (SIMPLIFIED)
# ============================================================================
# Servicio independiente para la gestión de stock e inventario

import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# =============================
# CONFIGURACIÓN DE LOGGING
# =============================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("stock-service")

# =============================
# EVENTOS DE CICLO DE VIDA
# =============================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Iniciando Stock Service")
    logger.info("📦 Módulos activos: inventory, articles, stock calculation")
    yield
    # Shutdown
    logger.info("🛑 Cerrando Stock Service")

# =============================
# INICIALIZACIÓN DE LA APP
# =============================
app = FastAPI(
    title="Stock Service",
    description="Servicio independiente para gestión de stock e inventario",
    version="1.0.0",
    docs_url="/stock/docs",
    redoc_url="/stock/redoc",
    lifespan=lifespan
)

# =============================
# CONFIGURACIÓN DE CORS
# =============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# HEALTH CHECK
# =============================
@app.get("/stock/health")
async def health_check():
    """Health check endpoint para el stock service"""
    return {
        "status": "healthy",
        "service": "stock-service", 
        "version": "1.0.0",
        "features": {
            "inventory_management": "active",
            "stock_calculation": "active",
            "articles_crud": "active",
            "real_time_updates": "active"
        }
    }

# =============================
# INFORMACIÓN DEL SERVICIO
# =============================
@app.get("/stock/info")
async def service_info():
    """Información detallada del stock service"""
    return {
        "name": "Stock Service",
        "description": "Servicio para gestión integral de inventario y stock",
        "features": [
            {
                "name": "inventory_management",
                "description": "Gestión completa de inventario",
                "endpoints": ["/stock/inventory/*"]
            },
            {
                "name": "stock_calculation",
                "description": "Cálculo de stock en tiempo real",
                "endpoints": ["/stock/api/calculate/*"]
            },
            {
                "name": "articles_crud",
                "description": "CRUD de artículos",
                "endpoints": ["/stock/articles/*"]
            }
        ],
        "database": {
            "schema": "stock_db",
            "tables": ["articles", "inventory", "stock_movements", "stock_levels"]
        }
    }

# =============================
# DEMO API ENDPOINTS
# =============================
@app.get("/stock/articles")
async def get_articles():
    """Demo endpoint - Lista de artículos"""
    return {
        "articles": [
            {"id": 1, "name": "Producto A", "stock": 100, "price": 25.50},
            {"id": 2, "name": "Producto B", "stock": 75, "price": 15.25},
            {"id": 3, "name": "Producto C", "stock": 200, "price": 8.75}
        ],
        "total": 3,
        "status": "demo_data"
    }

@app.get("/stock/inventory/summary")
async def get_inventory_summary():
    """Demo endpoint - Resumen del inventario"""
    return {
        "total_products": 3,
        "total_stock": 375,
        "low_stock_items": 1,
        "value_total": 4962.50,
        "last_updated": "2025-08-24T13:35:00Z",
        "status": "demo_data"
    }

# =============================
# PÁGINA PRINCIPAL
# =============================
@app.get("/")
async def root():
    """Página principal del stock service"""
    return {
        "message": "Stock Service - Gestión de Inventario",
        "version": "1.0.0",
        "docs": "/stock/docs",
        "health": "/stock/health",
        "info": "/stock/info"
    }

# =============================
# API DE COMUNICACIÓN CON CORE
# =============================
@app.get("/stock/auth/verify")
async def verify_with_core():
    """Endpoint para verificar autenticación con el core service"""
    return {
        "message": "Authentication verification with core service",
        "core_service_url": "http://localhost:8001/core/health",
        "status": "simulation"
    }

# =============================
# MANEJADOR DE ERRORES
# =============================
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error en Stock Service: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error in stock service",
            "detail": str(exc),
            "service": "stock-service"
        }
    )

# =============================
# EJECUCIÓN DEL SERVIDOR
# =============================
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando Stock Service en puerto 8002")
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8002,
        reload=False
    )
