# ============================================================================
# OBRAS SERVICE - MAIN APPLICATION
# ============================================================================
# Servicio independiente para la gestión de obras

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
logger = logging.getLogger("obras-service")

# =============================
# INICIALIZACIÓN DE LA APP
# =============================
app = FastAPI(
    title="Obras Service",
    description="Servicio independiente para gestión de obras y proyectos",
    version="1.0.0",
    docs_url="/obras/docs",
    redoc_url="/obras/redoc"
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
# TODO: Importar routers específicos de obras
# from .routers import obras_router, projects_router, tasks_router
# app.include_router(obras_router, prefix="/obras/api", tags=["obras"])
# app.include_router(projects_router, prefix="/obras/projects", tags=["projects"])
# app.include_router(tasks_router, prefix="/obras/tasks", tags=["tasks"])

# =============================
# HEALTH CHECK
# =============================
@app.get("/obras/health")
async def health_check():
    """Health check endpoint para el obras service"""
    return {
        "status": "healthy",
        "service": "obras-service",
        "version": "1.0.0",
        "features": {
            "project_management": "active",
            "task_tracking": "active",
            "resource_allocation": "active",
            "progress_monitoring": "active"
        }
    }

# =============================
# INFORMACIÓN DEL SERVICIO
# =============================
@app.get("/obras/info")
async def service_info():
    """Información detallada del obras service"""
    return {
        "name": "Obras Service",
        "description": "Servicio para gestión integral de obras y proyectos",
        "features": [
            {
                "name": "project_management",
                "description": "Gestión completa de proyectos",
                "endpoints": ["/obras/projects/*"]
            },
            {
                "name": "task_tracking",
                "description": "Seguimiento de tareas",
                "endpoints": ["/obras/tasks/*"]
            },
            {
                "name": "resource_allocation",
                "description": "Asignación de recursos",
                "endpoints": ["/obras/resources/*"]
            }
        ],
        "database": {
            "schema": "obras_db",
            "tables": ["projects", "tasks", "resources", "progress", "budgets"]
        }
    }

# =============================
# API DE COMUNICACIÓN CON CORE
# =============================
@app.get("/obras/auth/verify")
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
    logger.info("🚀 Iniciando Obras Service")
    logger.info("🏗️ Módulos activos: projects, tasks, resources, monitoring")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Cerrando Obras Service")

# =============================
# MANEJADOR DE ERRORES
# =============================
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error en Obras Service: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error in obras service",
            "detail": str(exc),
            "service": "obras-service"
        }
    )

# =============================
# EJECUCIÓN DEL SERVIDOR
# =============================
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando Obras Service en puerto 8003")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        reload=True
    )
