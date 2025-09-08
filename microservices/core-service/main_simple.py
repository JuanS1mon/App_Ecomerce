# ============================================================================
# CORE SERVICE - MAIN APPLICATION (SIMPLIFIED)
# ============================================================================
# Servicio principal que contiene los módulos CORE del sistema

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
logger = logging.getLogger("core-service")

# =============================
# EVENTOS DE CICLO DE VIDA
# =============================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Iniciando Core Service")
    logger.info("📋 Módulos activos: admin, security, mail, chat, mensajes")
    yield
    # Shutdown
    logger.info("🛑 Cerrando Core Service")

# =============================
# INICIALIZACIÓN DE LA APP
# =============================
app = FastAPI(
    title="Core Service",
    description="Servicio principal que contiene admin, security, mail, chat y mensajes",
    version="1.0.0",
    docs_url="/core/docs",
    redoc_url="/core/redoc",
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
@app.get("/core/health")
async def health_check():
    """Health check endpoint para el core service"""
    return {
        "status": "healthy",
        "service": "core-service",
        "version": "1.0.0",
        "modules": {
            "admin": "active",
            "security": "active", 
            "mail": "active",
            "chat": "active",
            "mensajes": "active"
        }
    }

# =============================
# INFORMACIÓN DEL SERVICIO
# =============================
@app.get("/core/info")
async def service_info():
    """Información detallada del core service"""
    return {
        "name": "Core Service",
        "description": "Servicio principal con módulos core del sistema",
        "modules": [
            {
                "name": "admin",
                "description": "Panel de administración general",
                "endpoints": ["/core/admin/*"]
            },
            {
                "name": "security", 
                "description": "Autenticación, autorización y JWT",
                "endpoints": ["/core/auth/*"]
            },
            {
                "name": "mail",
                "description": "Sistema de correos electrónicos", 
                "endpoints": ["/core/mail/*"]
            },
            {
                "name": "chat",
                "description": "Sistema de comunicación en tiempo real",
                "endpoints": ["/core/chat/*"]
            },
            {
                "name": "mensajes",
                "description": "Sistema de mensajes y notificaciones",
                "endpoints": ["/core/mensajes/*"]
            }
        ]
    }

# =============================
# PÁGINA PRINCIPAL
# =============================
@app.get("/")
async def root():
    """Página principal del core service"""
    return {
        "message": "Core Service - API Principal",
        "version": "1.0.0",
        "docs": "/core/docs",
        "health": "/core/health",
        "info": "/core/info"
    }

# =============================
# MANEJADOR DE ERRORES
# =============================
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error en Core Service: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error in core service",
            "detail": str(exc),
            "service": "core-service"
        }
    )

# =============================
# EJECUCIÓN DEL SERVIDOR
# =============================
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando Core Service en puerto 8001")
    uvicorn.run(
        "main_simple:app",  # Usar string import para reload
        host="0.0.0.0",
        port=8001,  # Puerto correcto para core service
        reload=False  # Deshabilitar reload para evitar warnings
    )
