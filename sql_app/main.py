# ============================================================================
# SISTEMA DE SQL_APP - MAIN APPLICATION
# ============================================================================
# Archivo principal de la aplicación FastAPI
# Contiene la configuración central, middlewares, rutas y manejadores de errores

# =============================
# CONFIGURACIÓN Y ENTORNO
# ======    import traceback

from sql_app.config import FRONTEND_URL, ORIGINS, STATIC_DIR, ENVIRONMENT
from sql_app.logging_config import setup_logging
import logging

# Configurar logging al inicio y forzar reconfiguración de todos los loggers
setup_logging()

# Forzar que todos los loggers existentes usen también el file handler
import logging.config
from sql_app.logging_config import LOGGING_CONFIG

# Reconfigurar todos los loggers para asegurar que usen el file handler
logging.config.dictConfig(LOGGING_CONFIG)

# Obtener logger principal para confirmar configuración
main_logger = logging.getLogger("main")
main_logger.info("🚀 Logging configurado - archivos se escribirán en logs/server.log")

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
from sql_app.Services.mensajes import router as mensajes_router
from sql_app.Services.mensajes.route_mensajes_admin import router as mensajes_admin_router
from sql_app.Services.mensajes.route_static import router as mensajes_static_router
from sql_app.Services.mensajes.websocket.router import router as websocket_router
from sql_app.Services.chat.route_chat_api import router as chat_api_router
from sql_app.Services.admin.route_admin_pages import router as admin_pages_router
from sql_app.Services.admin.route_admin_simple import router as admin_simple_router
from sql_app.Services.app_stock.route_config_stock import configure_stock_routes
from sql_app.Services.app_obras.route_config_obras import configure_obras_routes
from sql_app.Services.widgets.widget_loader import router as widgets_router

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

# Montar archivos estáticos de widgets
app.mount("/widgets/static", StaticFiles(directory="sql_app/Services/widgets/static"), name="widgets-static")

# Endpoint de prueba simple para verificar que funciona
@app.get("/test-simple")
async def test_simple_endpoint():
    return {"message": "Test endpoint works!", "timestamp": "2025-07-21"}

# Endpoint para probar widgets
@app.get("/test-widgets")
async def test_widgets_page():
    """Página de prueba para widgets de comunicación"""
    from fastapi.responses import FileResponse
    return FileResponse("test_widgets.html")

# Endpoint para el Editor Visual Avanzado - TEST DEBUG
@app.get("/editor-visual-test-debug")
async def editor_visual_test_debug():
    """Test debug para editor visual"""
    import os
    from fastapi.responses import HTMLResponse
    
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, "static", "html", "editor_visual.html")
    file_exists = os.path.exists(file_path)
    
    return HTMLResponse(f"""
    <html><body>
    <h1>Debug Editor Visual</h1>
    <p>Directorio actual: {current_dir}</p>
    <p>Ruta del archivo: {file_path}</p>
    <p>¿Archivo existe?: {file_exists}</p>
    <p>Listado de static/html/:</p>
    <ul>
    """)

# Endpoint para el Editor Visual Avanzado - NUEVO ENDPOINT SIN CONFLICTOS
@app.get("/editor-visual-nuevo")
async def editor_visual_nuevo():
    """Editor Visual Avanzado - Diseñador de esquemas de base de datos"""
    try:
        with open("static/html/editor_visual.html", "r", encoding="utf-8") as f:
            from fastapi.responses import HTMLResponse
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        from fastapi.responses import HTMLResponse
        return HTMLResponse("""
        <html><body>
        <h1>Editor Visual No Disponible</h1>
        <p>Archivo no encontrado: static/html/editor_visual.html</p>
        </body></html>
        """, status_code=404)

# Endpoint para el Editor Visual Avanzado - COMENTADO porque está en router
# @app.get("/editor-visual")
# async def editor_visual_page():
#     """Editor Visual Avanzado - Diseñador de esquemas de base de datos"""
#     from fastapi.responses import FileResponse
#     import os
#     file_path = os.path.join(os.getcwd(), "static", "html", "editor_visual.html")
#     return FileResponse(file_path)

# Endpoint para listar rutas registradas
@app.get("/debug/routes")
async def debug_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": getattr(route, 'name', 'unknown')
            })
    return {"routes": routes}

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

# Endpoint de prueba para verificar que las rutas de API funcionan
@app.get("/api/test")
async def test_api():
    return {"message": "API funciona correctamente", "timestamp": "2025-07-21"}

@app.get("/api/mensajes/test")
async def test_mensajes_api():
    return {"message": "Ruta de mensajes funciona", "total_mensajes": 14}

# Endpoint de información de rutas disponibles
@app.get("/routes-info")
async def routes_info():
    """Información de rutas disponibles en el sistema"""
    return {
        "rutas_publicas": {
            "administracion_mensajes": "http://127.0.0.1:8000/mensajes-admin-public",
            "chat_test": "http://127.0.0.1:8000/chat-test",
            "widgets_demo": "http://127.0.0.1:8000/widgets-demo",
            "editor_visual": "http://127.0.0.1:8000/editor-visual",
            "documentacion": "http://127.0.0.1:8000/docs",
            "home": "http://127.0.0.1:8000/"
        },
        "rutas_protegidas": {
            "admin_mensajes": "http://127.0.0.1:8000/admin/mensajes",
            "panel_admin": "http://127.0.0.1:8000/admin"
        },
        "apis": {
            "mensajes": "http://127.0.0.1:8000/api/mensajes/",
            "admin_mensajes": "http://127.0.0.1:8000/admin/api/mensajes/",
            "widgets": "http://127.0.0.1:8000/widgets/"
        },
        "websockets": {
            "chat": "ws://127.0.0.1:8000/chat/ws/room/{room_id}",
            "notificaciones": "ws://127.0.0.1:8000/mensajes/ws/notifications/{user_id}"
        },
        "widgets": {
            "loader": "http://127.0.0.1:8000/widgets/loader.js",
            "message_widget_css": "http://127.0.0.1:8000/widgets/static/css/message-widget.css",
            "message_widget_js": "http://127.0.0.1:8000/widgets/static/js/message-widget.js",
            "chat_widget_css": "http://127.0.0.1:8000/widgets/static/css/chat-widget.css",
            "chat_widget_js": "http://127.0.0.1:8000/widgets/static/js/chat-widget.js"
        }
    }

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

# Logging específico para el router de mensajes - MOVIDO AL PRINCIPIO
logger.info("🔔 Registrando router de mensajes...")
try:
    app.include_router(mensajes_router)
    logger.info(f"✅ Router de mensajes registrado con prefix: {mensajes_router.prefix}")
    # Verificar rutas registradas
    rutas_mensajes = [route for route in app.routes if hasattr(route, 'path') and '/api/mensajes' in route.path]
    logger.info(f"📋 {len(rutas_mensajes)} rutas de mensajes registradas")
except Exception as e:
    logger.error(f"❌ Error al registrar router de mensajes: {e}")
    import traceback
    
# Registrar router de administración de mensajes
logger.info("🛠️ Registrando router de administración de mensajes...")
try:
    app.include_router(mensajes_admin_router)
    logger.info(f"✅ Router de administración de mensajes registrado con prefix: {mensajes_admin_router.prefix}")
except Exception as e:
    logger.error(f"❌ Error al registrar router de admin mensajes: {e}")
    import traceback

# Registrar router de archivos estáticos de mensajes
logger.info("📁 Registrando router de archivos estáticos de mensajes...")
try:
    app.include_router(mensajes_static_router)
    logger.info(f"✅ Router de estáticos de mensajes registrado con prefix: {mensajes_static_router.prefix}")
except Exception as e:
    logger.error(f"❌ Error al registrar router de estáticos mensajes: {e}")
    import traceback

# Registrar router de API de chat
logger.info("💬 Registrando router de API de chat...")
try:
    app.include_router(chat_api_router)
    logger.info(f"✅ Router de API de chat registrado con prefix: {chat_api_router.prefix}")
except Exception as e:
    logger.error(f"❌ Error al registrar router de API de chat: {e}")
    import traceback

# Registrar router WebSocket de mensajes
logger.info("🔌 Registrando router WebSocket de mensajes...")
try:
    app.include_router(websocket_router)
    logger.info(f"✅ Router WebSocket de mensajes registrado con prefix: {websocket_router.prefix}")
except Exception as e:
    logger.error(f"❌ Error al registrar router WebSocket mensajes: {e}")
    import traceback

# Registrar router WebSocket de chat
logger.info("💬 Registrando router WebSocket de chat...")
try:
    from sql_app.Services.chat.websocket.router import router as chat_websocket_router
    app.include_router(
        chat_websocket_router,
        prefix="/chat",
        tags=["chat-websocket"]
    )
    logger.info("✅ Router WebSocket de chat registrado con prefix: /chat")
except Exception as e:
    logger.error(f"❌ Error al registrar router WebSocket chat: {e}")
    import traceback

# Registrar router API REST del chat
logger.info("💬 Registrando router API REST del chat...")
try:
    from sql_app.Services.chat.api_router import router as chat_api_router
    app.include_router(
        chat_api_router,
        tags=["chat-api"]
    )
    logger.info("✅ Router API REST del chat registrado")
except Exception as e:
    logger.error(f"❌ Error al registrar router API del chat: {e}")

# Registrar archivos estáticos del chat
logger.info("📁 Registrando archivos estáticos del chat...")
try:
    from fastapi.staticfiles import StaticFiles
    app.mount("/static/chat", StaticFiles(directory="sql_app/Services/chat"), name="chat-static")
    logger.info("✅ Archivos estáticos del chat registrados en /static/chat")
except Exception as e:
    logger.error(f"❌ Error al registrar archivos estáticos del chat: {e}")
    import traceback

# Endpoint directo para la página de pruebas del chat
logger.info("🧪 Registrando endpoint directo para página de pruebas de chat...")
try:
    @app.get("/chat-test")
    async def serve_chat_test_page():
        """Servir la página HTML de pruebas del sistema de chat"""
        from fastapi.responses import FileResponse
        import os
        
        test_file_path = os.path.join("sql_app", "Services", "chat", "test_chat_system.html")
        if os.path.exists(test_file_path):
            return FileResponse(
                path=test_file_path,
                media_type="text/html",
                filename="test_chat_system.html"
            )
        else:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail=f"Archivo no encontrado en: {test_file_path}")
    
    # Endpoint público para admin mensajes (sin autenticación)
    @app.get("/mensajes-admin-public")
    async def serve_admin_mensajes_public():
        """Servir la página de administración de mensajes sin autenticación"""
        from fastapi.responses import FileResponse
        import os
        
        html_file = os.path.join("sql_app", "Services", "mensajes", "frontend", "admin", "mensajes.html")
        if os.path.exists(html_file):
            return FileResponse(html_file, media_type="text/html")
        else:
            # Fallback al archivo en static
            html_file_static = os.path.join("sql_app", "static", "admin", "mensajes.html")
            if os.path.exists(html_file_static):
                return FileResponse(html_file_static, media_type="text/html")
            else:
                from fastapi import HTTPException
                raise HTTPException(status_code=404, detail=f"Archivo no encontrado")

    # Endpoint para demo de widgets
    @app.get("/widgets-demo")
    async def serve_widgets_demo():
        """Servir la página de demostración de widgets"""
        from fastapi.responses import FileResponse
        import os
        
        demo_file = os.path.join("sql_app", "Services", "widgets", "demo.html")
        if os.path.exists(demo_file):
            return FileResponse(demo_file, media_type="text/html")
        else:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail=f"Archivo demo no encontrado")
    
    logger.info("✅ Endpoints /chat-test y /mensajes-admin-public registrados correctamente")
except Exception as e:
    logger.error(f"❌ Error al registrar endpoint de chat: {e}")
    import traceback
    traceback.print_exc()

# Endpoints públicos para testing del sistema de mensajes (sin autenticación)
logger.info("🧪 Registrando endpoints de testing para mensajes...")
try:
    @app.get("/api/test/hello")
    async def test_hello():
        """Endpoint simple de prueba"""
        return {"message": "Hello, testing!", "status": "OK"}
    
    @app.get("/api/test/mensajes/no-leidos/count")
    async def test_contador_mensajes_public():
        """Endpoint público para testing del contador de mensajes"""
        try:
            from sqlalchemy.orm import Session
            from sql_app.db.database import get_db
            from sql_app.Services.mensajes.crud_mensajes import CrudMensajes
            
            # Usar una sesión de base de datos directa
            db_gen = get_db()
            db = next(db_gen)
            try:
                # Usar un usuario de prueba o devolver datos ficticios
                count = 3  # Datos ficticios para testing
                return {"count": count, "test": True}
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error en test contador mensajes: {e}")
            return {"count": 0, "test": True, "error": str(e)}
    
    @app.get("/api/test/mensajes/navbar")
    async def test_mensajes_navbar_public():
        """Endpoint público para testing de mensajes del navbar"""
        try:
            # Devolver datos ficticios para testing
            mensajes_test = [
                {
                    "id": 1,
                    "titulo": "Mensaje de prueba 1",
                    "contenido": "Este es un mensaje de prueba",
                    "tipo": "sistema",
                    "prioridad": "normal",
                    "leido": False,
                    "fecha_creacion": "2025-07-21T20:00:00Z",
                    "nombre_emisor": "Sistema"
                },
                {
                    "id": 2,
                    "titulo": "Notificación importante",
                    "contenido": "Esta es una notificación de prueba",
                    "tipo": "alerta",
                    "prioridad": "alta",
                    "leido": True,
                    "fecha_creacion": "2025-07-21T19:30:00Z",
                    "nombre_emisor": "Admin"
                }
            ]
            return mensajes_test
        except Exception as e:
            logger.error(f"Error en test mensajes navbar: {e}")
            return []
    
    @app.get("/api/test/auth/me")
    async def test_auth_me_public():
        """Endpoint público para testing de autenticación"""
        return {
            "usuario": {
                "id": 1,
                "username": "test_user",
                "email": "test@example.com",
                "is_admin": True,
                "codigo": "TEST001"
            },
            "test": True
        }
    
    logger.info("✅ Endpoints de testing para mensajes registrados correctamente")
except Exception as e:
    logger.error(f"❌ Error al registrar endpoints de testing: {e}")
    import traceback
    traceback.print_exc()

# Endpoints públicos para testing de mensajes sin autenticación (usando usuario juan)
logger.info("🧪 Registrando endpoints públicos para testing de mensajes...")
try:
    @app.get("/api/public/mensajes/no-leidos/count")
    async def public_contador_mensajes():
        """Endpoint público para testing del contador de mensajes usando usuario juan"""
        try:
            from sqlalchemy.orm import Session
            from sql_app.db.database import get_db
            from sql_app.Services.mensajes.crud_mensajes import CrudMensajes
            
            db_gen = get_db()
            db = next(db_gen)
            try:
                # Buscar usuario juan para testing
                from sql_app.db.models.config.usuarios import Usuarios
                usuario_juan = db.query(Usuarios).filter(Usuarios.usuario == "juan").first()
                if usuario_juan:
                    count = CrudMensajes.contar_mensajes_no_leidos(db, usuario_juan.codigo)
                    return {"count": count, "test": True, "usuario": "juan"}
                else:
                    return {"count": 0, "test": True, "error": "Usuario juan no encontrado"}
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error en contador público mensajes: {e}")
            return {"count": 0, "test": True, "error": str(e)}
    
    @app.get("/api/public/mensajes/navbar")
    async def public_mensajes_navbar():
        """Endpoint público para testing de mensajes del navbar usando usuario juan"""
        try:
            from sqlalchemy.orm import Session
            from sql_app.db.database import get_db
            from sql_app.Services.mensajes.crud_mensajes import CrudMensajes
            
            db_gen = get_db()
            db = next(db_gen)
            try:
                # Buscar usuario juan para testing
                from sql_app.db.models.config.usuarios import Usuarios
                usuario_juan = db.query(Usuarios).filter(Usuarios.usuario == "juan").first()
                if usuario_juan:
                    mensajes = CrudMensajes.get_mensajes_navbar(db, usuario_juan.codigo)
                    return mensajes
                else:
                    return []
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error en mensajes navbar público: {e}")
            return []
    
    @app.get("/api/public/auth/me")
    async def public_auth_me():
        """Endpoint público para simular autenticación con usuario juan"""
        try:
            from sqlalchemy.orm import Session
            from sql_app.db.database import get_db
            
            db_gen = get_db()
            db = next(db_gen)
            try:
                from sql_app.db.models.config.usuarios import Usuarios
                usuario_juan = db.query(Usuarios).filter(Usuarios.usuario == "juan").first()
                if usuario_juan:
                    return {
                        "usuario": {
                            "id": usuario_juan.codigo,
                            "username": usuario_juan.usuario,
                            "email": usuario_juan.mail,
                            "is_admin": True,  # Para testing
                            "codigo": usuario_juan.codigo
                        },
                        "test": True
                    }
                else:
                    return {"error": "Usuario juan no encontrado", "test": True}
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error en auth público: {e}")
            return {"error": str(e), "test": True}
    
    @app.get("/api/public/mensajes/estadisticas")
    async def public_estadisticas_mensajes():
        """Endpoint público para estadísticas de mensajes usando usuario juan"""
        try:
            from sqlalchemy.orm import Session
            from sql_app.db.database import get_db
            from sql_app.Services.mensajes.crud_mensajes import CrudMensajes
            
            db_gen = get_db()
            db = next(db_gen)
            try:
                from sql_app.db.models.config.usuarios import Usuarios
                usuario_juan = db.query(Usuarios).filter(Usuarios.usuario == "juan").first()
                if usuario_juan:
                    # Obtener estadísticas básicas
                    total_mensajes = CrudMensajes.contar_todos_mensajes(db, usuario_juan.codigo)
                    mensajes_no_leidos = CrudMensajes.contar_mensajes_no_leidos(db, usuario_juan.codigo)
                    
                    # Simular otras estadísticas
                    return {
                        "total_mensajes": total_mensajes,
                        "mensajes_no_leidos": mensajes_no_leidos,
                        "mensajes_urgentes": 1,  # Simulado
                        "usuarios_activos": 1,
                        "test": True
                    }
                else:
                    return {
                        "total_mensajes": 0,
                        "mensajes_no_leidos": 0,
                        "mensajes_urgentes": 0,
                        "usuarios_activos": 0,
                        "test": True
                    }
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error en estadísticas públicas: {e}")
            return {
                "total_mensajes": 0,
                "mensajes_no_leidos": 0,
                "mensajes_urgentes": 0,
                "usuarios_activos": 0,
                "error": str(e),
                "test": True
            }
    
    logger.info("✅ Endpoints públicos de mensajes registrados correctamente")
except Exception as e:
    logger.error(f"❌ Error al registrar endpoints públicos: {e}")
    import traceback
    traceback.print_exc()

# Registrar router de widgets
logger.info("🧩 Registrando router de widgets...")
try:
    app.include_router(widgets_router)
    logger.info(f"✅ Router de widgets registrado con prefix: {widgets_router.prefix}")
except Exception as e:
    logger.error(f"❌ Error al registrar router de widgets: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    logger.error(f"❌ Error al registrar endpoint de chat: {e}")
    import traceback
    traceback.print_exc()
    
# Registrar router de páginas de administración
logger.info("📄 Registrando router de páginas de administración...")
try:
    app.include_router(admin_pages_router)
    logger.info(f"✅ Router de páginas de administración registrado con prefix: {admin_pages_router.prefix}")
except Exception as e:
    logger.error(f"❌ Error al registrar router de páginas admin: {e}")
    import traceback

# Registrar router simple de administración (sin autenticación)
logger.info("🔓 Registrando router simple de administración...")
try:
    app.include_router(admin_simple_router)
    logger.info(f"✅ Router simple de administración registrado con prefix: {admin_simple_router.prefix}")
except Exception as e:
    logger.error(f"❌ Error al registrar router simple admin: {e}")
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")

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

# =============================
# ENDPOINTS DE PÁGINAS DE PRUEBA
# =============================

@app.get("/chat/prueba")
async def chat_prueba():
    """Página de prueba del sistema de chat"""
    try:
        with open("chat_prueba.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html><body style='font-family: Arial; padding: 50px;'>
        <h1>🚫 Página de Chat no encontrada</h1>
        <p>La página chat_prueba.html no se encuentra en el directorio raíz.</p>
        <p><a href='/admin/mensajes'>← Volver a mensajes</a></p>
        </body></html>
        """)

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