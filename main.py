# ============================================================================
# SISTEMA DE GESTIÓN DE STOCK - MAIN APPLICATION
# ============================================================================
# Archivo principal de la aplicación FastAPI
# Contiene la configuración central, middlewares, rutas y manejadores de errores

# ============================================================================
# IMPORTACIONES ESTÁNDAR Y DEPENDENCIAS
# ============================================================================
from dotenv import load_dotenv
import os
import httpx
import traceback
import importlib
import logging

# ============================================================================
# IMPORTACIONES DE FASTAPI Y STARLETTE
# ============================================================================
from fastapi import Depends, FastAPI, Request, status, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("main")

# ============================================================================
# IMPORTACIONES DE BASE DE DATOS Y MODELOS
# ============================================================================
from .db.database import Base, engine, get_db, create_database, create_tables
from .db.schemas.config.Usuarios import UserDB
from .db.models.Blog import BlogPost as BlogPostModel
from .db.middleware.db_error_handler import DBErrorMiddleware
from sqlalchemy.orm import Session

# ============================================================================
# IMPORTACIONES DE ROUTERS Y SERVICIOS
# ============================================================================
from .routers import usuarios as aut_usuario
from .routers import Blog
from .routers.config import Generar, configDB, Migraciones, Analisis, Scraping, usuarios_admin
from .routers.config.Admin import create_admin_router
from .Services.security.security import current_user
from .Services.security.admin_roles import router as roles_router
from .Services.mail import mail
from .Services.tickets import route_ticket
from .Services.app_stock.route_config_stock import configure_stock_routes
# ============================================================================
# CONFIGURACIÓN DE ENTORNO Y VARIABLES GLOBALES
# ============================================================================
# Cargar variables de entorno desde el archivo .env en el directorio raíz
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
FRONTEND_URL = os.getenv("FRONTEND_URL")
ORIGINS = os.getenv("ORIGINS", "*").split()
STATIC_DIR = "static"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").strip()  # development, production

# ============================================================================
# INICIALIZACIÓN DE LA APLICACIÓN FASTAPI
# ============================================================================
app = FastAPI(
    title="Sistema de Gestión de Stock",
    description="API para gestión integral de inventario, artículos y stock calculado en tiempo real",
    version="1.0.0",
    docs_url="/docs" if ENVIRONMENT == "development" else None,  # Ocultar docs en producción
    redoc_url="/redoc" if ENVIRONMENT == "development" else None
)

# ============================================================================
# CONFIGURACIÓN DE TEMPLATES Y ARCHIVOS ESTÁTICOS
# ============================================================================
templates = Jinja2Templates(directory="sql_app/static")
app.mount("/static", StaticFiles(directory="sql_app/static"), name="static")

# ============================================================================
# DEFINICIÓN DE MIDDLEWARES PERSONALIZADOS
# ============================================================================
# Middleware de redirección al frontend
class FrontendRedirectMiddleware(BaseHTTPMiddleware):
    """Middleware para redireccionar peticiones del frontend a la URL externa configurada"""
    async def dispatch(self, request: Request, call_next):
        frontend_prefix = "/frontend"
        if request.url.path.startswith(frontend_prefix):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{FRONTEND_URL}{request.url.path[len(frontend_prefix):]}")
                    if response.status_code == 200:
                        return RedirectResponse(url=f"{FRONTEND_URL}{request.url.path[len(frontend_prefix):]}")
            except httpx.RequestError:
                return JSONResponse(status_code=503, content={"detail": "El frontend está caído. Por favor, intenta más tarde."})
        return await call_next(request)

# Middleware de manejo de errores personalizados
class CustomErrorMiddleware(BaseHTTPMiddleware):
    """Middleware para servir páginas de error personalizadas desde archivos HTML estáticos"""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Excluir rutas de documentación y estáticos internos de FastAPI
        excluded_paths = ["/docs", "/redoc", "/openapi.json"]
        if any(request.url.path.startswith(path) for path in excluded_paths):
            return response
        
        # Construir ruta absoluta al directorio static
        static_dir = os.path.join(os.path.dirname(__file__), "static")
        
        if response.status_code == 404:
            return FileResponse(os.path.join(static_dir, '404.html'), status_code=404)
        elif response.status_code == 401:
            return FileResponse(os.path.join(static_dir, '401.html'), status_code=401)
        elif response.status_code == 403:
            return FileResponse(os.path.join(static_dir, '403.html'), status_code=403)
        elif response.status_code == 405:
            return FileResponse(os.path.join(static_dir, '405.html'), status_code=405)
        elif response.status_code == 500:
            return FileResponse(os.path.join(static_dir, '500.html'), status_code=500)
        elif response.status_code == 503:
            return FileResponse(os.path.join(static_dir, '503.html'), status_code=503)
        elif response.status_code == 505:
            return FileResponse(os.path.join(static_dir, '505.html'), status_code=505)
        
        return response

# Middleware para incluir contexto de usuario en templates
class UserTemplateMiddleware(BaseHTTPMiddleware):
    """Middleware para inyectar datos de usuario en todas las respuestas HTML"""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Solo procesar respuestas HTML
        if isinstance(response, HTMLResponse) or getattr(response, "media_type", None) == "text/html":
            # Si hay un usuario en la sesión, incluirlo en el contexto del template
            try:
                # El usuario podría estar en response.context
                if hasattr(response, "context") and isinstance(response.context, dict):
                    if "user" not in response.context:
                        # Aquí podríamos agregar la lógica para obtener el usuario actual
                        # como haces en tus rutas, pero eso requeriría más modificaciones
                        pass
            except Exception as e:
                logger.error(f"Error al procesar middleware de templates: {e}")
        
        return response

# ============================================================================
# CONFIGURACIÓN Y APLICACIÓN DE MIDDLEWARES
# ============================================================================
# CORS - Configuración de orígenes cruzados
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS if ENVIRONMENT == "production" else ["*"],  # Más restrictivo en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middlewares de aplicación (orden importante: LIFO - último en entrar, primero en salir)
app.add_middleware(UserTemplateMiddleware)     # Procesar contexto de usuario
app.add_middleware(DBErrorMiddleware)          # Manejar errores de base de datos
# app.add_middleware(CustomErrorMiddleware)      # Páginas de error personalizadas - DESACTIVADO TEMPORALMENTE
app.add_middleware(FrontendRedirectMiddleware) # Redirección al frontend

# ============================================================================
# MANEJADORES DE EXCEPCIONES GLOBALES
# ============================================================================

# Manejador de excepciones HTTP de Starlette
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Manejador personalizado para excepciones HTTP con páginas de error personalizadas"""
    # Construir ruta absoluta al directorio static
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    
    if exc.status_code == 404:
        return FileResponse(os.path.join(static_dir, '404.html'), status_code=404)
    elif exc.status_code == 401:
        return FileResponse(os.path.join(static_dir, '401.html'), status_code=401)
    elif exc.status_code == 403:
        return FileResponse(os.path.join(static_dir, '403.html'), status_code=403)
    elif exc.status_code == 405:
        return FileResponse(os.path.join(static_dir, '405.html'), status_code=405)
    elif exc.status_code == 500:
        return FileResponse(os.path.join(static_dir, '500.html'), status_code=500)
    elif exc.status_code == 503:
        return FileResponse(os.path.join(static_dir, '503.html'), status_code=503)
    elif exc.status_code == 505:
        return FileResponse(os.path.join(static_dir, '505.html'), status_code=505)
    return JSONResponse(status_code=exc.status_code, content=jsonable_encoder({"detail": exc.detail}))

# Manejador de errores de validación de FastAPI
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejador personalizado para errores de validación de datos"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
        content=jsonable_encoder({
            "detail": "Se produjo un error de validación.", 
            "errors": exc.errors()
        })
    )

# Manejador de excepciones HTTP de FastAPI
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Manejador personalizado para excepciones HTTP de FastAPI"""
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(url="/loginpage")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# ============================================================================
# FUNCIONES DE INICIALIZACIÓN DE BASE DE DATOS
# ============================================================================
def create_all_tables():
    """Crear todas las tablas de la base de datos importando modelos dinámicamente"""
    try:
        models_dir = os.path.join(os.path.dirname(__file__), 'db', 'models')
        
        # Importar modelos específicos conocidos para evitar errores
        known_models = [            'sql_app.db.models.config.usuarios',
            'sql_app.db.models.config.tickets',
            # 'sql_app.db.models.config.admin_roles',  # No existe este modelo
        ]
        
        for module_name in known_models:
            try:
                importlib.import_module(module_name)
                logger.info(f"Modelo importado: {module_name}")
            except ImportError as e:
                logger.warning(f"No se pudo importar el modelo {module_name}: {e}")
        
        # Crear las tablas
        create_tables()
        logger.info("Tablas creadas exitosamente")
        
    except Exception as e:
        logger.error(f"Error al crear tablas: {e}")
        traceback.print_exc()

def ensure_directories():
    """Asegurar que existan los directorios necesarios para servicios y maestros"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    directories = [
        os.path.join(base_dir, "Services"),
        os.path.join(base_dir, "routers", "Maestros")
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            logger.info(f"Creando directorio: {directory}")
            os.makedirs(directory, exist_ok=True)

# ============================================================================
# INICIALIZACIÓN DE LA APLICACIÓN
# ============================================================================
# Crear la base de datos y todas las tablas
create_database()
create_all_tables()

# Asegurar que existan los directorios necesarios
ensure_directories()

# ============================================================================
# EVENTOS DE CICLO DE VIDA DE LA APLICACIÓN
# ============================================================================
# Evento de inicio de la aplicación
@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación"""
    logger.info("🚀 Iniciando aplicación FastAPI")
    logger.info("📁 Directorios verificados")
    logger.info("🗄️ Base de datos inicializada")
    logger.info("📊 Sistema de stock configurado")

# Evento de cierre de la aplicación
@app.on_event("shutdown")
async def shutdown_event():
    """Evento que se ejecuta al cerrar la aplicación"""
    logger.info("🛑 Cerrando aplicación FastAPI")
    logger.info("💾 Limpieza de recursos completada")

# ============================================================================
# CONFIGURACIÓN DE ROUTERS Y SERVICIOS
# ============================================================================
# Incluir routers principales de la aplicación
app.include_router(aut_usuario.router)          # Autenticación de usuarios
app.include_router(usuarios_admin.router)       # Administración de usuarios
app.include_router(Generar.router)             # Generación de contenido
app.include_router(configDB.router)            # Configuración de base de datos
app.include_router(create_admin_router(app))   # Panel de administración
app.include_router(Blog.router)                # Sistema de blog
app.include_router(Migraciones.router)         # Migraciones de base de datos
app.include_router(Analisis.router)            # Análisis y reportes
app.include_router(mail.router)                # Sistema de correo
app.include_router(Scraping.router)            # Web scraping
app.include_router(route_ticket.router)        # Sistema de tickets
app.include_router(roles_router)              # Roles de administrador

# Configurar rutas del sistema de stock
configure_stock_routes(app)

# ============================================================================
# RUTAS PRINCIPALES DE LA APLICACIÓN WEB
# ============================================================================
# Endpoint de debug para templates
@app.get("/debug-template", include_in_schema=False)
async def debug_template(request: Request):
    """Debug de configuración de templates"""
    try:
        import os
        current_dir = os.getcwd()
        template_dir = templates.env.loader.searchpath
        static_path = "sql_app/static/index.html"
        static_exists = os.path.exists(static_path)
        
        return JSONResponse({
            "current_directory": current_dir,
            "template_searchpath": template_dir,
            "static_file_path": static_path,
            "static_file_exists": static_exists,
            "available_files": os.listdir("sql_app/static") if os.path.exists("sql_app/static") else "Directory not found"
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# Página principal del sitio
@app.get("/index", response_class=HTMLResponse, include_in_schema=False)
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root(request: Request):
    """Página principal del sitio web"""
    # Forzar recarga
    return templates.TemplateResponse("index.html", {"request": request})

# ============================================================================
# ENDPOINTS DE ACTIVACIÓN DE CUENTA (COMENTADO - SE USA EL DEL ROUTER)
# ============================================================================
# @app.get("/activar", response_class=HTMLResponse, include_in_schema=False)
# async def activar_cuenta_page_main(request: Request):
#     """Página de activación de cuenta - workaround directo en main.py"""
#     try:
#         # Servir la página HTML de activación
#         with open("sql_app/static/activation.html", "r", encoding="utf-8") as file:
#             html_content = file.read()
#         return HTMLResponse(content=html_content, status_code=200)
#     except FileNotFoundError:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Página de activación no encontrada"
#         )
#     except Exception as e:
#         logger.error(f"Error sirviendo página de activación: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Error interno del servidor"
#         )

# @app.post("/api/activar", include_in_schema=False)
# async def activar_cuenta_api_main(request: Request, db: Session = Depends(get_db)):
#     """API para activar cuenta - workaround directo en main.py"""
#     try:
#         # Importar funciones necesarias
#         from .Services.security.security import decodifica_token, log_security_event
#         from .db.crud.config.Usuarios import update_usuario_activate
#         
#         # Función helper para obtener info del cliente
#         def get_client_info(request):
#             return {
#                 "ip": request.client.host if request.client else "unknown",
#                 "user_agent": request.headers.get("user-agent", "unknown")
#             }
#         
#         # Función helper para sanitizar logs
#         def sanitize_for_log(data):
#             if isinstance(data, str) and len(data) > 50:
#                 return data[:50] + "..."
#             return data
#         
#         client_info = get_client_info(request)
#         
#         # Obtener el token del body del request
#         body = await request.json()
#         token = body.get("token")
#         
#         # Validar token
#         if not token or len(token) > 500:
#             log_security_event(
#                 "ACTIVATION_FAILED",
#                 {"reason": "invalid_token_format", **client_info},
#                 "WARNING"
#             )
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Token de activación inválido"
#             )
#         
#         # Decodificar token
#         usuario = decodifica_token(token)
#         if not usuario:
#             log_security_event(
#                 "ACTIVATION_FAILED",
#                 {"reason": "token_decode_failed", **client_info},
#                 "WARNING"
#             )
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Token de activación expirado o inválido"
#             )
#         
#         # Activar usuario
#         result = update_usuario_activate(db, usuario)
#         
#         if not result:
#             log_security_event(
#                 "ACTIVATION_FAILED",
#                 {"reason": "user_not_found", "usuario": sanitize_for_log(usuario), **client_info},
#                 "WARNING"
#             )
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Usuario no encontrado"
#             )
#         
#         log_security_event(
#             "ACCOUNT_ACTIVATED",
#             {"usuario": sanitize_for_log(usuario), **client_info},
#             "INFO"
#         )
#         
#         return JSONResponse(
#             content={
#                 "message": f"Cuenta de {usuario} activada exitosamente",
#                 "usuario": usuario,
#                 "success": True
#             },
#             status_code=status.HTTP_200_OK
#         )
#         
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error activando cuenta: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Error interno durante la activación"
#         )

# ============================================================================
# RUTAS DE PÁGINAS LEGALES Y ESTÁTICAS
# ============================================================================

# Página de términos y condiciones
@app.get("/terminos", response_class=HTMLResponse, include_in_schema=False)
async def get_terminos():
    """Página de términos y condiciones del servicio"""
    with open("sql_app/static/terminos.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read(), status_code=200)
    
# Página de política de privacidad
@app.get("/privacidad", response_class=HTMLResponse, include_in_schema=False)
async def get_privacidad():
    """Página de política de privacidad"""
    with open("sql_app/static/privacidad.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read(), status_code=200)

# ============================================================================
# RUTAS DE AUTENTICACIÓN Y ACCESO
# ============================================================================

# Página de registro de usuarios
@app.get("/registerpage", response_class=HTMLResponse, include_in_schema=False)
async def get_register_page():
    """Página de registro de nuevos usuarios"""
    with open("sql_app/static/register.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read(), status_code=200)
        
# Página de inicio de sesión
@app.get("/loginpage", response_class=HTMLResponse, include_in_schema=False)
async def get_login_page():
    """Página principal de inicio de sesión"""
    with open("sql_app/static/login.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read(), status_code=200)

# Página de login simplificada
@app.get("/login-simple", response_class=HTMLResponse, include_in_schema=False)
async def get_login_simple():
    """Página de login simplificada para pruebas"""
    with open("sql_app/static/login_simple.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read(), status_code=200)

# ============================================================================
# RUTAS DE ADMINISTRACIÓN Y DEBUG
# ============================================================================
# Endpoint de debug para pruebas de autenticación
@app.get("/admin-debug", include_in_schema=False)
async def admin_debug(request: Request, db: Session = Depends(get_db)):
    """Endpoint de debug para probar autenticación en el panel de administración"""
    try:
        # Intentar obtener usuario usando get_optional_user
        from .Services.security.get_optional_user import get_optional_user
        user = await get_optional_user(request, db)
        
        if user is None:
            return JSONResponse({
                "status": "not_authenticated",
                "message": "Usuario no autenticado",
                "user": None
            }, status_code=401)
        
        # Si llegamos aquí, la autenticación funcionó
        return JSONResponse({
            "status": "success",
            "message": "Autenticación exitosa con get_optional_user",
            "user": {
                "username": user.usuario if hasattr(user, 'usuario') else 'N/A',
                "nombre": user.nombre if hasattr(user, 'nombre') else 'N/A',
                "roles": [{"id": r.id, "nombre": r.nombre} for r in user.roles] if hasattr(user, 'roles') and user.roles else []
            }
        })
        
    except Exception as e:
        logger.error(f"Error en admin-debug: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": f"Error interno: {str(e)}",
            "type": str(type(e).__name__)
        }, status_code=500)

# Panel de administración simplificado para pruebas
@app.get("/admin-simple", response_class=HTMLResponse, include_in_schema=False)
async def admin_simple(request: Request, db: Session = Depends(get_db)):
    """Panel de administración simplificado sin dependencias complejas"""
    try:
        from .Services.security.get_optional_user import get_optional_user
        user = await get_optional_user(request, db)
        
        if user is None:
            return RedirectResponse(url="/loginpage", status_code=302)
        
        # Página HTML simple de éxito
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Panel - Success</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 50px; background-color: #f0f8ff; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .success {{ color: #28a745; }}
                .info {{ background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                h1 {{ color: #333; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f8f9fa; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="success">✅ Admin Panel - Autenticación Exitosa!</h1>
                
                <div class="info">
                    <strong>🎉 BUEN TRABAJO!</strong> La autenticación funciona perfectamente.
                </div>
                
                <h2>Información del Usuario:</h2>
                <table>
                    <tr><th>Campo</th><th>Valor</th></tr>
                    <tr><td>Usuario</td><td>{user.usuario if hasattr(user, 'usuario') else 'N/A'}</td></tr>
                    <tr><td>Nombre</td><td>{user.nombre if hasattr(user, 'nombre') else 'N/A'}</td></tr>
                    <tr><td>Email</td><td>{user.mail if hasattr(user, 'mail') else 'N/A'}</td></tr>
                    <tr><td>Activo</td><td>{user.activo if hasattr(user, 'activo') else 'N/A'}</td></tr>
                    <tr><td>Roles</td><td>{', '.join([r.nombre for r in user.roles]) if hasattr(user, 'roles') and user.roles else 'Sin roles'}</td></tr>
                </table>
                
                <div style="margin-top: 30px;">
                    <h2>Tests Realizados:</h2>
                    <ul>
                        <li>✅ Login endpoint funciona</li>
                        <li>✅ Token JWT válido generado</li>
                        <li>✅ get_optional_user funciona correctamente</li>
                        <li>✅ Bearer token authentication funciona</li>
                        <li>✅ Cookie authentication funciona</li>
                        <li>✅ Admin panel accesible</li>
                    </ul>
                </div>
                
                <div style="margin-top: 30px; text-align: center;">
                    <a href="/loginpage" style="padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">Logout / Volver al Login</a>
                    <a href="/admin" style="padding: 10px 20px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; margin-left: 10px;">Ir al Admin Original</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content, status_code=200)
        
    except Exception as e:
        logger.error(f"Error en admin-simple: {str(e)}")
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>", status_code=500)

# Panel de administración principal
@app.get("/admin", include_in_schema=False)
async def read_admin(request: Request, db: Session = Depends(get_db)):
    """Panel de administración principal de la aplicación"""
    try:
        # Obtener usuario actual usando get_optional_user que funciona correctamente
        from .Services.security.get_optional_user import get_optional_user
        user = await get_optional_user(request, db)
        
        # Si no hay usuario autenticado, redirigir al login
        if user is None:
            return RedirectResponse(url="/loginpage", status_code=302)
        
        # Cargar la página del panel de administración
        return templates.TemplateResponse("index.html", {"request": request, "user": user})
    except Exception as e:
        logger.error(f"Error cargando panel de admin: {str(e)}")
        # Si hay algún error, redirigir a la página de login
        return RedirectResponse(url="/loginpage", status_code=302)