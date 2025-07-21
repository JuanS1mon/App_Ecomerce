# ============================================================================
# SISTEMA DE SQL_APP - MAIN APPLICATION
# ============================================================================
# Archivo principal de la aplicación FastAPI
# Contiene la configuración central, middlewares, rutas y manejadores de errores

# =============================
# CONFIGURACIÓN Y ENTORNO
# =============================
from sql_app.config import FRONTEND_URL, ORIGINS, STATIC_DIR, ENVIRONMENT
from sql_app.logging_config import setup_logging

setup_logging()

# =============================
# IMPORTACIONES ESTÁNDAR Y FASTAPI
# =============================
import sys
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi import Request, Depends
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

# =============================
# IMPORTACIONES DE MIDDLEWARES Y HANDLERS
# =============================
from sql_app.middleware.custom import (
    RequestLoggingMiddleware, FrontendRedirectMiddleware, CustomErrorMiddleware, UserTemplateMiddleware, DebugMiddleware
)
from sql_app.exception_handlers import register_exception_handlers
from sql_app.middleware.jwt_middleware import JWTMiddleware

# =============================
# IMPORTACIONES DE DB Y ROUTERS
# =============================
from sql_app.db.database import get_db, create_database, create_tables, run_alembic_upgrade
from sql_app.init_app import create_all_tables, ensure_directories
from sql_app.routers import usuarios as aut_usuario
from sql_app.routers import auth as auth_router
from sql_app.routers import Blog
from sql_app.routers.config import Generar, configDB, Migraciones, Analisis, Scraping, usuarios_admin
from sql_app.routers.config.Admin import router as admin_router
from sql_app.routers import frontend_pages
from sql_app.Services.security.admin_roles import router as roles_router
from sql_app.Services.mail.mail import MAIL_CONFIG_OK, router as mail_router
from sql_app.Services.tickets import route_ticket
from sql_app.Services.app_stock.route_config_stock import configure_stock_routes
from sql_app.Services.app_obras.route_config_obras import configure_obras_routes

# Importar todos los modelos para SQLAlchemy
from sql_app.db import models_import

from sql_app.routers.static_pages import router as static_pages_router
from sql_app.logging_config import LOG_CONFIG
from sql_app.app_settings import CORS_CONFIG, DOCS_URL, REDOC_URL

# =============================
# INICIALIZACIÓN DE LA APP
# =============================
app = FastAPI(
    title="Sistema de Gestión de Stock",
    description="API para gestión integral de inventario, artículos y stock calculado en tiempo real",
    version="1.0.0",
    docs_url=DOCS_URL,
    redoc_url=REDOC_URL
)

app.mount("/static", StaticFiles(directory="sql_app/static"), name="static")

# =============================
# MIDDLEWARES
# =============================
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# Phase 2: Importar nuevos middlewares de rendimiento
from sql_app.middleware.rate_limit import RateLimitMiddleware
from sql_app.monitoring.metrics import MetricsMiddleware

# Compresión gzip para mejorar performance
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Middleware de métricas (debe ir primero para capturar todo)
app.add_middleware(MetricsMiddleware)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_CONFIG["allow_origins"],
    allow_credentials=CORS_CONFIG["allow_credentials"],
    allow_methods=CORS_CONFIG["allow_methods"],
    allow_headers=CORS_CONFIG["allow_headers"],
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(DebugMiddleware)
app.add_middleware(JWTMiddleware)

# =============================
# EXCEPTION HANDLERS
# =============================
register_exception_handlers(app)

# =============================
# HEALTH CHECK ENDPOINT
# =============================
from datetime import datetime
from sql_app.monitoring.metrics import metrics_endpoint

@app.get("/health", include_in_schema=False)
async def health_check():
    """Endpoint de salud para load balancers y monitoreo"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": ENVIRONMENT
    }

# Endpoint de métricas para Prometheus
@app.get("/metrics", include_in_schema=False)
async def prometheus_metrics():
    """Endpoint de métricas para Prometheus"""
    return await metrics_endpoint()

# Phase 3: Endpoint de health avanzado
@app.get("/health/detailed", include_in_schema=False)
async def detailed_health_check():
    """Health check detallado con múltiples verificaciones"""
    return await get_health_status()

# =============================
# INICIALIZACIÓN DE BASE DE DATOS Y DIRECTORIOS
# =============================
import logging
logger = logging.getLogger("main")

# Validación de configuración de correo
def check_mail_config():
    return MAIL_CONFIG_OK

# Manejo amigable de errores al crear la base de datos
db_status = True
modelos_status = True
try:
    create_database()
except Exception as e:
    db_status = False
    msg = str(e)
    if "Error de inicio de sesión" in msg or "login failed" in msg.lower():
        logger.error("No se pudo conectar a la base de datos. Verifica usuario y contraseña.")
    elif "ya existe" in msg.lower() or "already exists" in msg.lower():
        pass  # No loguear, solo reflejar en checklist
    else:
        logger.error(f"Error al crear la base de datos: {e}")

# Manejo amigable de errores al crear las tablas
tablas_status = True
try:
    create_all_tables(create_tables, logger)
except Exception as e:
    tablas_status = False
    msg = str(e)
    if "ya existe" in msg.lower() or "already exists" in msg.lower():
        pass  # No loguear, solo reflejar en checklist
    else:
        logger.error(f"Error al crear tablas: {e}")

ensure_directories()

# =============================
# EVENTOS DE CICLO DE VIDA
# =============================
# Phase 2: Importar inicializadores de optimización
from sql_app.cache.redis_cache import cache_manager
from sql_app.monitoring.metrics import init_metrics
from sql_app.utils.sql_optimizer import init_sql_optimizations

# Phase 3: Importar sistemas de monitoreo avanzado
from sql_app.monitoring.health_checks import init_health_checks, get_health_status
from sql_app.monitoring.backup_manager import init_backup_system
from sql_app.monitoring.notifications import notification_manager

@app.on_event("startup")
async def startup_event():
    alembic_ok = run_alembic_upgrade()
    mail_ok = check_mail_config()
    
    # Phase 2: Inicializar sistemas de rendimiento
    try:
        cache_manager.initialize()
        cache_ok = True
    except Exception as e:
        logger.warning(f"⚠️ Cache no disponible: {e}")
        cache_ok = False
    
    try:
        init_metrics()
        metrics_ok = True
    except Exception as e:
        logger.warning(f"⚠️ Métricas no disponibles: {e}")
        metrics_ok = False
    
    try:
        await init_sql_optimizations()
        sql_opt_ok = True
    except Exception as e:
        logger.warning(f"⚠️ Optimizaciones SQL fallaron: {e}")
        sql_opt_ok = False
    
    # Phase 3: Inicializar sistemas de monitoreo avanzado
    try:
        await init_health_checks()
        health_checks_ok = True
    except Exception as e:
        logger.warning(f"⚠️ Health checks no disponibles: {e}")
        health_checks_ok = False
    
    try:
        init_backup_system()
        backup_ok = True
    except Exception as e:
        logger.warning(f"⚠️ Sistema de backup no disponible: {e}")
        backup_ok = False
    
    # Enviar notificación de inicio
    try:
        await notification_manager.send_alert({
            'severity': 'info',
            'summary': 'Sistema iniciado correctamente',
            'description': f'Aplicación iniciada en modo {ENVIRONMENT}',
            'service': 'system-startup'
        })
    except Exception as e:
        logger.warning(f"⚠️ Notificaciones no disponibles: {e}")
    
    checklist = [
        ("🟢 .env cargado correctamente", True),
        ("🟢 Configuración de base de datos cargada", db_status),
        ("🟢 Configuración de correo cargada correctamente", mail_ok),
        ("🟢 Modelos importados", modelos_status),
        ("🟢 Tablas creadas/verificadas", tablas_status),
        ("🟢 Directorios verificados", True),
        ("🟢 Sistema de stock configurado", True),
        ("🟢 Middlewares y rutas registradas", True),
        ("🟢 Logging inicializado", True),
        ("🟢 Migraciones Alembic aplicadas", alembic_ok),
        ("🚀 Sistema de cache inicializado", cache_ok),
        ("📊 Sistema de métricas inicializado", metrics_ok),
        ("⚡ Optimizaciones SQL aplicadas", sql_opt_ok),
        ("🔍 Health checks avanzados", health_checks_ok),
        ("💾 Sistema de backup configurado", backup_ok),
    ]
    logger.info("\n================= CHECKLIST DE INICIO =================")
    for item, ok in checklist:
        logger.info(f"{'✅' if ok else '⚠️'} {item}")
    logger.info("======================================================\n")
    logger.info("🚀 Iniciando aplicación FastAPI")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Cerrando aplicación FastAPI")
    
    # Phase 2: Limpiar recursos de cache
    try:
        from sql_app.cache.redis_cache import cache_manager
        if hasattr(cache_manager, 'close'):
            await cache_manager.close()
    except Exception as e:
        logger.warning(f"⚠️ Error cerrando cache: {e}")
    
    logger.info("💾 Limpieza de recursos completada")

# =============================
# REGISTRO DE ROUTERS
# =============================
app.include_router(aut_usuario.router)
app.include_router(aut_usuario.usuarios_router)
app.include_router(auth_router.router)
app.include_router(usuarios_admin.router)
app.include_router(Generar.router)
app.include_router(configDB.router)
app.include_router(admin_router)
app.include_router(frontend_pages.router)
app.include_router(Blog.router)
app.include_router(Migraciones.router)
app.include_router(Analisis.router)
app.include_router(mail_router)
app.include_router(Scraping.router)
app.include_router(route_ticket.router)
app.include_router(roles_router)
app.include_router(static_pages_router)
from sql_app.routers.usuarios import usuarios_router
app.include_router(usuarios_router)
configure_stock_routes(app)
configure_obras_routes(app)

# Importar y registrar el router de restablecimiento de contraseña
from sql_app.routers.password_reset import router as password_reset_router
app.include_router(password_reset_router)

# ============================================================================# ============================================================================
# EJECUCIÓN DEL SERVIDOR
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando servidor FastAPI")
    logger.info("🔗 Servidor disponible en: http://localhost:8000")
    logger.info("📚 Documentación API en: http://localhost:8000/docs")
    logger.info("🛡️ Admin panel en: http://localhost:8000/admin")
    logger.info("⚠️  Usa Ctrl+C para detener el servidor")
    try:
        # Configuración optimizada para producción
        uvicorn.run(
            app=app,
            host="0.0.0.0",
            port=int(os.getenv("PORT", "8000")),
            workers=int(os.getenv("WORKERS", "1")),
            reload=False,
            log_level=os.getenv("LOG_LEVEL", "info"),
            access_log=ENVIRONMENT == "development",
            use_colors=ENVIRONMENT == "development",
            log_config=LOG_CONFIG
        )
    except KeyboardInterrupt:
        logger.info("🛑 Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error al iniciar servidor: {str(e)}")