# ============================================================================
# STOCK SERVICE - MAIN APPLICATION  
# ============================================================================
# Servicio independiente para la gestión de stock e inventario

import sys
import os
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
# INICIALIZACIÓN DE LA APP
# =============================
app = FastAPI(
    title="Stock Service",
    description="Servicio independiente para gestión de stock e inventario",
    version="1.0.0",
    docs_url="/stock/docs",
    redoc_url="/stock/redoc"
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
# IMPORTACIÓN DE ROUTERS
# =============================
# TODO: Importar routers específicos del stock
# from .routers import stock_router, inventory_router, articles_router
# app.include_router(stock_router, prefix="/stock/api", tags=["stock"])
# app.include_router(inventory_router, prefix="/stock/inventory", tags=["inventory"])
# app.include_router(articles_router, prefix="/stock/articles", tags=["articles"])

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
# API DE COMUNICACIÓN CON CORE
# =============================
@app.get("/stock/auth/verify")
async def verify_with_core():
    """Endpoint para verificar autenticación con el core service"""
    # TODO: Implementar comunicación con core service para autenticación
    return {
        "message": "Authentication verification with core service",
        "core_service_url": "http://core-service:8001/core/auth/verify"
    }

# =============================
# EVENTOS DE CICLO DE VIDA
# =============================
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Iniciando Stock Service")
    logger.info("📦 Módulos activos: inventory, articles, stock calculation")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Cerrando Stock Service")

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
        app,
        host="0.0.0.0",
        port=8002,
        reload=True
    )
