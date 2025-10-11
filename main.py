# ============================================================================
# SISTEMA DE SQL_APP - MAIN APPLICATION
# ============================================================================
# Archivo principal de la aplicación FastAPI
# Contiene la configuración central, middlewares, rutas y manejadores de errores

# =============================
# CONFIGURACIÓN Y ENTORNO
# =============================
from config import FRONTEND_URL, ORIGINS, STATIC_DIR, ENVIRONMENT
from logging_config_new import setup_logging

# CONFIGURAR LOGGING ULTRA VERBOSO
setup_logging()

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

# =============================
# IMPORTACIONES DE MIDDLEWARES Y HANDLERS
# =============================
from middleware.custom import (
    RequestLoggingMiddleware, FrontendRedirectMiddleware, CustomErrorMiddleware, UserTemplateMiddleware, DebugMiddleware
)
from exception_handlers import register_exception_handlers
from middleware.jwt_middleware import JWTMiddleware

# =============================
# IMPORTACIONES DE DB Y ROUTERS
# =============================
from db.database import get_db, create_database, create_tables, run_alembic_upgrade
from init_app import create_all_tables, ensure_directories
from routers import usuarios as aut_usuario
from routers import auth as auth_router
from routers import Blog
from routers.config import Generar, configDB, Migraciones, Analisis, Scraping, usuarios_admin
from routers.config import AdminNew as admin_router
from routers.config.Admin import router as admin_router
from routers import frontend_pages
from Services.security.admin_roles import router as roles_router
from Services.mail.mail import MAIL_CONFIG_OK, router as mail_router
from Services.tickets import route_ticket
from Services.app_stock.route_config_stock import configure_stock_routes
from Services.app_obras.route_config_obras import configure_obras_routes

from routers.static_pages import router as static_pages_router
from logging_config import LOG_CONFIG
from app_settings import CORS_CONFIG, DOCS_URL, REDOC_URL

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

# --------------------------------------------------------------------------
# Favicon handler: evita error 500 si el navegador solicita /favicon.ico
# Sirve logo.svg como fallback (o 204 si no está disponible)
# --------------------------------------------------------------------------
@app.get("/favicon.ico")
async def favicon():
    candidate_svg = os.path.join("sql_app", "static", "logo.svg")
    candidate_png = os.path.join("sql_app", "static", "img", "favicon.png")
    if os.path.exists(candidate_png):
        return FileResponse(candidate_png)
    if os.path.exists(candidate_svg):
        return FileResponse(candidate_svg, media_type="image/svg+xml")
    return Response(status_code=204)

# =============================
# MIDDLEWARES
# =============================
from fastapi.middleware.cors import CORSMiddleware
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

# =============================
# EVENTOS DE CICLO DE VIDA
# =============================
@app.on_event("startup")
async def startup_event():
    alembic_ok = run_alembic_upgrade()
    mail_ok = check_mail_config()
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
    ]
    logger.info("\n================= CHECKLIST DE INICIO =================")
    for item, ok in checklist:
        logger.info(f"{'✅' if ok else '❌'} {item}")
    logger.info("======================================================\n")
    logger.info("🚀 Iniciando aplicación FastAPI")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Cerrando aplicación FastAPI")
    logger.info("💾 Limpieza de recursos completada")

# =============================
# REGISTRO DE ROUTERS
# =============================
app.include_router(aut_usuario.router)
app.include_router(aut_usuario.usuarios_router)
app.include_router(auth_router.router)
app.include_router(usuarios_admin.router)
app.include_router(Generar.router)

# CONFIGURADOR AUTO DE RUTAS MULTI-TABLA - BIBLIOTECA SISTEMA
try:
    from Services.biblioteca_sistema.route_config_biblioteca_sistema import configure_biblioteca_sistema_routes
    configure_biblioteca_sistema_routes(app)
    print("✅ Sistema biblioteca_sistema configurado exitosamente")
    print("🔗 Accede a: http://localhost:8000/static/html/forms/biblioteca_sistema/index.html")
except Exception as e:
    print(f"⚠️ Sistema biblioteca_sistema no disponible: {e}")

# ROUTER TEMPORAL PARA PROBAR GENERADOR OPTIMIZADO
try:
    from routers.config.generador_test_optimizado import router as generador_optimizado_router
    app.include_router(generador_optimizado_router)
    print("✅ Router de generador optimizado agregado exitosamente")
except Exception as e:
    print(f"⚠️ No se pudo cargar el router optimizado: {e}")

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
from routers.usuarios import usuarios_router
app.include_router(usuarios_router)
configure_stock_routes(app)
configure_obras_routes(app)

# Importar y registrar el router de restablecimiento de contraseña
from routers.password_reset import router as password_reset_router
app.include_router(password_reset_router)

# ENDPOINT DE PRUEBA PARA PROFILE
@app.get("/api/test-user")
async def test_user_simple():
    """Endpoint simple para probar la funcionalidad del avatar"""
    return {
        "id": 1,
        "username": "juan",
        "email": "juan@test.com",
        "nombre": "Juan",
        "apellido": "Test",
        "imagen_perfil": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iMjAiIGZpbGw9IiM0Yjc2ODgiLz4KPHRleHQgeD0iMjAiIHk9IjI2IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTZweCIgZm9udC13ZWlnaHQ9ImJvbGQiIGZpbGw9IndoaXRlIj5KPC90ZXh0Pgo8L3N2Zz4=",
        "telefono": "123456789",
        "direccion": "Test Address 123"
    }

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
        uvicorn.run(
            app=app,
            host="0.0.0.0",
            port=8001,
            reload=False,
            log_level="debug",  # Cambiado a debug para más logs
            access_log=True,    # Habilitar access logs
            use_colors=True,    # Usar colores en los logs
            log_config=LOG_CONFIG
        )
    except KeyboardInterrupt:
        logger.info("🛑 Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error al iniciar servidor: {str(e)}")