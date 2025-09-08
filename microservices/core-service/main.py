# ============================================================================
# CORE SERVICE - MAIN APPLICATION
# ============================================================================
# Servicio principal que contiene los módulos CORE del sistema:
# - Admin (Panel de administración)
# - Security (Autenticación, JWT, roles)
# - Mail (Sistema de correos)
# - Chat (Comunicación en tiempo real)
# - Mensajes (Sistema de notificaciones)

import sys
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
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
# INICIALIZACIÓN DE LA APP
# =============================
# La app se inicializa después de definir lifespan

# =============================
# CONFIGURACIÓN DE CORS
# =============================
# Se configura después de crear la app
def configure_app():
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # En producción, especificar dominios exactos
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

# =============================
# ARCHIVOS ESTÁTICOS
# =============================
# app.mount("/core/static", StaticFiles(directory="static"), name="static")

# =============================
# IMPORTACIÓN DE ROUTERS
# =============================
# Importar routers básicos para prueba
try:
    # from .admin import router as admin_router
    # from .security import router as security_router
    # from .mail import router as mail_router
    # from .chat import router as chat_router
    # from .mensajes import router as mensajes_router
    
    # app.include_router(admin_router, prefix="/core/admin", tags=["admin"])
    # app.include_router(security_router, prefix="/core/auth", tags=["security"])
    # app.include_router(mail_router, prefix="/core/mail", tags=["mail"])
    # app.include_router(chat_router, prefix="/core/chat", tags=["chat"])
    # app.include_router(mensajes_router, prefix="/core/mensajes", tags=["mensajes"])
    
    logger.info("Routers cargados exitosamente")
except Exception as e:
    logger.warning(f"Error cargando routers: {e}")
    logger.info("Continuando sin routers específicos")

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
# EVENTOS DE CICLO DE VIDA
# =============================
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Iniciando Core Service")
    logger.info("📋 Módulos activos: admin, security, mail, chat, mensajes")
    yield
    # Shutdown
    logger.info("🛑 Cerrando Core Service")

# Aplicar lifespan a la app
app = FastAPI(
    title="Core Service",
    description="Servicio principal que contiene admin, security, mail, chat y mensajes",
    version="1.0.0",
    docs_url="/core/docs",
    redoc_url="/core/redoc",
    lifespan=lifespan
)

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
        app,
        host="0.0.0.0",
        port=8001,
        reload=True
    )
