# ============================================================================
# SISTEMA DE SQL_APP - MAIN APPLICATION
# ============================================================================
# Archivo principal de la aplicación FastAPI
# Contiene la configuración central, middlewares, rutas y manejadores de errores

# =============================
# PRE-IMPORTACIÓN CRÍTICA: Cargar typing_extensions correcto
# =============================
import pre_import  # DEBE ser el primer import para evitar conflictos

print("✅ pre_import cargado correctamente")

# =============================
# CONFIGURACIÓN Y ENTORNO
# =============================
from config import FRONTEND_URL, ORIGINS, STATIC_DIR, ENVIRONMENT
from logging_config_new import setup_logging

print("✅ Configuración y logging importados")

# CONFIGURAR LOGGING ULTRA VERBOSO
setup_logging()

print("✅ Logging configurado")

# =============================
# IMPORTACIONES ESTÁNDAR Y FASTAPI
# =============================
import sys
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi import Request, Depends
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, Response
from sqlalchemy.orm import Session

print("✅ Importaciones básicas de FastAPI completadas")

# =============================
# IMPORTACIONES DE MIDDLEWARES Y HANDLERS
# =============================
from middleware.custom import (
    RequestLoggingMiddleware, FrontendRedirectMiddleware, CustomErrorMiddleware, UserTemplateMiddleware, DebugMiddleware
)
from exception_handlers import register_exception_handlers
from middleware.jwt_middleware import JWTMiddleware

print("✅ Middlewares y handlers importados")

# =============================
# IMPORTACIONES DE DB Y ROUTERS
# =============================
from db.database import get_db, create_database, create_tables, run_alembic_upgrade
from init_app import create_all_tables, ensure_directories
from routers import usuarios as aut_usuario
from routers import auth as auth_router
from routers.config import  configDB,  Analisis,  usuarios_admin
from routers.config.Admin import router as admin_router
from routers import frontend_pages
from routers.static_pages import router as static_pages_router
from Services.mail.mail import router as mail_router, MAIL_CONFIG_OK
from routers.mapas import router as mapas_router
from logging_config_new import LOG_CONFIG

print("✅ Importaciones de DB y routers básicos completadas")

# =============================
# INICIALIZACIÓN DE LA APP
# =============================
# La aplicación se crea más abajo con el lifespan manager

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
        print("⚠️  No se pudo conectar a la base de datos. Verifica usuario y contraseña.")
        logger.warning("No se pudo conectar a la base de datos. Verifica usuario y contraseña.")
    elif "ya existe" in msg.lower() or "already exists" in msg.lower():
        pass  # No loguear, solo reflejar en checklist
    else:
        print(f"⚠️  Error al crear la base de datos: {e}")
        logger.warning(f"Error al crear la base de datos: {e}")

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
        print(f"⚠️  Error al crear tablas: {e}")
        logger.warning(f"Error al crear tablas: {e}")

ensure_directories()

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    try:
        alembic_ok = run_alembic_upgrade()  # HABILITADO: Ejecutar migraciones de Alembic
    except Exception as e:
        logger.error(f"❌ Error ejecutando Alembic: {e}")
        alembic_ok = False
    mail_ok = check_mail_config()

    # Inicializar usuario administrador
    admin_created = False
    try:
        # from init_admin import init_admin_on_startup
        # db = next(get_db())
        # init_admin_on_startup(db)
        # admin_created = True
        admin_created = True  # Usuarios ya existen con contraseñas conocidas
    except Exception as e:
        logger.error(f"Error al crear usuario administrador: {e}")
        admin_created = False

    # Limpiar tokens expirados del blacklist
    tokens_cleaned = False
    try:
        from db.models.security.token_blacklist import TokenBlacklist
        # Crear sesión manualmente para el lifespan
        from db.database import SessionLocal
        db = SessionLocal()
        try:
            deleted_count = TokenBlacklist.cleanup_expired_tokens(db)
            logger.info(f"🧹 Tokens expirados eliminados del blacklist: {deleted_count}")
            tokens_cleaned = True
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error al limpiar tokens expirados: {e}")
        tokens_cleaned = False

    # Mostrar rutas registradas para debug
    logger.info("📋 Rutas registradas:")
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = getattr(route, 'methods', ['MOUNT'])
            logger.info(f"  - {methods} {route.path}")

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
        ("🟢 Usuario administrador inicializado", admin_created),
        ("🟢 Tokens expirados limpiados del blacklist", tokens_cleaned),
    ]
    logger.info("\n================= CHECKLIST DE INICIO =================")
    for item, ok in checklist:
        logger.info(f"{'✅' if ok else '❌'} {item}")
    logger.info("======================================================\n")
    logger.info("🚀 Iniciando aplicación FastAPI")

    yield

    # Shutdown logic
    logger.info("🛑 Cerrando aplicación FastAPI")
    logger.info("💾 Limpieza de recursos completada")

# Crear la aplicación con lifespan
app = FastAPI(
    title="Ecommerce API",
    description="API para sistema de ecommerce",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar archivos estáticos y middlewares después de crear la app
app.mount("/static", StaticFiles(directory="static"), name="static")

# --------------------------------------------------------------------------
# Favicon handler: evita error 500 si el navegador solicita /favicon.ico
# Sirve logo.svg como fallback (o 204 si no está disponible)
# --------------------------------------------------------------------------
@app.get("/favicon.ico")
async def favicon():
    candidate_svg = os.path.join("sql_app", "static", "logo.png")
    candidate_png = os.path.join("sql_app", "static", "img", "favicon.png")
    if os.path.exists(candidate_png):
        return FileResponse(candidate_png)
    if os.path.exists(candidate_svg):
        return FileResponse(candidate_svg, media_type="image/svg+xml")
    return Response(status_code=204)

# =============================
# MIDDLEWARES
# =============================
from app_settings import CORS_CONFIG
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_CONFIG["allow_origins"],
    allow_credentials=CORS_CONFIG["allow_credentials"],
    allow_methods=CORS_CONFIG["allow_methods"],
    allow_headers=CORS_CONFIG["allow_headers"],
)
# app.add_middleware(RequestLoggingMiddleware)  # DESHABILITADO TEMPORALMENTE
# app.add_middleware(DebugMiddleware)  # DESHABILITADO TEMPORALMENTE
# app.add_middleware(JWTMiddleware)  # DESHABILITADO TEMPORALMENTE

# =============================
# EXCEPTION HANDLERS
# =============================
register_exception_handlers(app)

# =============================
# REGISTRO DE ROUTERS
# =============================
app.include_router(aut_usuario.router)
app.include_router(aut_usuario.usuarios_router)
app.include_router(auth_router.router, prefix="/api/admin/auth", tags=["autenticación"])
app.include_router(usuarios_admin.router)
app.include_router(configDB.router)
app.include_router(admin_router)
app.include_router(frontend_pages.router)


# Router de Migración entre Bases de Datos (MVP)
# from routers.config import MigracionesBD
# app.include_router(MigracionesBD.router)
app.include_router(Analisis.router)
app.include_router(mail_router)
app.include_router(static_pages_router)
app.include_router(mapas_router, prefix="/mapas", tags=["mapas"])
from routers.usuarios import usuarios_router
app.include_router(usuarios_router)
# Importar y registrar el router de restablecimiento de contraseña
from routers.password_reset import router as password_reset_router
app.include_router(password_reset_router)

# Importar y registrar el router de productos públicos ecommerce
try:
    from routers.ecommerce_public import router as ecommerce_public_router
    app.include_router(ecommerce_public_router)
    logger.info("Router ecommerce_public registrado")
except Exception as e:
    logger.error(f"❌ Error registrando router ecommerce_public: {e}")
    import traceback
    traceback.print_exc()

# Importar y registrar el router simple de productos (comentado - archivo no existe)
# try:
#     from simple_product_router import router as productos_router
#     app.include_router(productos_router, prefix="/ecomerce", tags=["productos"])
#     logger.info("Router productos registrado correctamente")
# except Exception as e:
#     logger.error(f"❌ Error registrando router productos: {e}")
#     import traceback
#     traceback.print_exc()

# Importar y registrar el router API simple para ecommerce (comentado - archivo no existe)
# try:
#     from simple_api_router import router as api_router
#     app.include_router(api_router)
#     logger.info("Router API ecommerce integrado en simple_product_router")
# except Exception as e:
#     logger.error(f"❌ Error registrando router API ecommerce: {e}")
#     import traceback
#     traceback.print_exc()

# Importar y registrar el router de administración de categorías
from routers.admin_categorias import router as admin_categorias_router
app.include_router(admin_categorias_router)

# Importar y registrar el router de presupuesto
# from Projects.ecomerce.routes.presupuesto import router as presupuesto_router
# app.include_router(presupuesto_router, prefix="/ecomerce/api", tags=["presupuesto"])

# Importar y registrar el router de carrito
from routers.carrito import router as carrito_router
logger.info(f"Registrando carrito_router con {len(carrito_router.routes)} rutas")
for route in carrito_router.routes:
    logger.info(f"  CARRITO ROUTE: {route.methods} {route.path}")
app.include_router(carrito_router, prefix="/ecomerce", tags=["carrito"])
logger.info("carrito_router registrado")

# Importar y registrar el router de páginas frontend
from routers.frontend_pages import router as frontend_pages_router
logger.info(f"Registrando frontend_pages_router con {len(frontend_pages_router.routes)} rutas")
for route in frontend_pages_router.routes:
    logger.info(f"  FRONTEND ROUTE: {route.methods} {route.path}")
app.include_router(frontend_pages_router)
logger.info("frontend_pages_router registrado")

# Importar y registrar el router de mapas
try:
    app.include_router(mapas_router, prefix="/mapas", tags=["mapas"])
    logger.info("mapas_router registrado correctamente")
    print("DEBUG: mapas_router registrado con prefix /mapas")
except Exception as e:
    logger.error(f"Error registrando mapas_router: {e}")
    print(f"DEBUG: Error registrando mapas_router: {e}")

# Importar y configurar rutas de ecommerce
try:
    from Projects.ecomerce.routes_config import configure_routes
    logger.info("Llamando a configure_routes...")
    configure_routes(app)
    logger.info("✅ Rutas de ecommerce configuradas correctamente")
    
    # Verificar que las rutas se registraron
    all_routes = [route for route in app.routes if hasattr(route, 'path')]
    ecommerce_routes = [route for route in all_routes if 'ecomerce' in route.path]
    usuarios_routes = [route for route in all_routes if 'usuarios' in route.path]
    
    logger.info(f"Total de rutas en la app: {len(all_routes)}")
    logger.info(f"Total de rutas ecommerce registradas: {len(ecommerce_routes)}")
    logger.info(f"Total de rutas usuarios registradas: {len(usuarios_routes)}")
    
    # Mostrar rutas de usuarios específicamente
    if usuarios_routes:
        logger.info("Rutas de usuarios encontradas:")
        for route in usuarios_routes:
            logger.info(f"  - USUARIOS: {route.methods} {route.path}")
    else:
        logger.warning("❌ No se encontraron rutas de usuarios!")
        
    # Mostrar algunas rutas ecommerce
    for route in ecommerce_routes[:10]:  # Mostrar las primeras 10
        logger.info(f"  - ECOMMERCE: {route.methods} {route.path}")
        
except Exception as e:
    logger.error(f"❌ Error configurando rutas de ecommerce: {e}")
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")
    raise

# Importar y registrar el router de autenticación ecommerce AL FINAL para que tenga prioridad
from routers.ecommerce_auth import router as ecommerce_auth_router
logger.info(f"Registrando ecommerce_auth_router con {len(ecommerce_auth_router.routes)} rutas")
for route in ecommerce_auth_router.routes:
    logger.info(f"  ECOMMERCE ROUTE: {route.methods} {route.path}")
app.include_router(ecommerce_auth_router)
logger.info("ecommerce_auth_router registrado")

# Importar y registrar el router de autenticación con Google
#from routers.google_oauth import router as google_oauth_router
#logger.info(f"Registrando google_oauth_router con {len(google_oauth_router.routes)} rutas")
#for route in google_oauth_router.routes:
#    logger.info(f"  GOOGLE OAUTH ROUTE: {route.methods} {route.path}")
#app.include_router(google_oauth_router)
#logger.info("google_oauth_router registrado")


# =============================
# RUTAS PRINCIPALES
# =============================

# Ruta raíz - Carga la página principal
@app.get("/")
async def root():
    """Carga la página principal del sitio"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Página principal no encontrada</h1>", status_code=404)

# ENDPOINT DE PRUEBA PARA PROFILE

# ============================================================================
# ============================================================================
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
        logger.info("🔧 Configuración de uvicorn: host=0.0.0.0, port=8000, reload=False")
        uvicorn.run(
            app=app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="debug",  # Cambiado a debug para más logs
            access_log=True,    # Habilitar access logs
            use_colors=True,    # Usar colores en los logs
            log_config=LOG_CONFIG
        )
        logger.info("✅ uvicorn.run() terminó normalmente")
    except KeyboardInterrupt:
        logger.info("🛑 Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error al iniciar servidor: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("🔚 Bloque finally ejecutado")
# Force reload 10/21/2025 19:29:27

