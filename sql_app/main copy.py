from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request, status, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

import os
import httpx
import traceback
import importlib
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("main")

# Importamos nuestro gestor de servicios
try:
    from ...Services.services_manager import ServicesManager
except ImportError:
    from sql_app.Services.services_manager import ServicesManager
# Importa lógica y módulos
try:
    from ...db.database import Base, engine, get_db, create_database, create_tables
except ImportError:
    from sql_app.db.database import Base, engine, get_db, create_database, create_tables
# Importar middleware de manejo de errores de base de datos
try:
    from ...db.middleware.db_error_handler import DBErrorMiddleware
except ImportError:
    from sql_app.db.middleware.db_error_handler import DBErrorMiddleware
# Rutas de los servicios core
try:
    from ...Services.security.admin_roles import router as roles_router
except ImportError:
    from sql_app.Services.security.admin_roles import router as roles_router
# Configuración de entorno
load_dotenv()
FRONTEND_URL = os.getenv("FRONTEND_URL")
ORIGINS = os.getenv("ORIGINS", "*").split()
STATIC_DIR = "static"

# Inicializar aplicación
app = FastAPI()

# Configurar plantillas
templates = Jinja2Templates(directory="static")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Middleware de redirección al frontend
class FrontendRedirectMiddleware(BaseHTTPMiddleware):
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

# Middleware de error personalizado
class CustomErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if response.status_code == 404:
            return FileResponse('static/404.html', status_code=404)
        elif response.status_code == 401:
            return FileResponse('static/401.html', status_code=401)
        elif response.status_code == 403:
            return FileResponse('static/403.html', status_code=403)
        elif response.status_code == 500:
            return FileResponse('static/500.html', status_code=500)
        elif response.status_code == 503:
            return FileResponse('static/503.html', status_code=503)
        elif response.status_code == 505:
            return FileResponse('static/505.html', status_code=505)
        
        return response

# Agregar middlewares a la app
app.add_middleware(DBErrorMiddleware)  # Agregar primero nuestro middleware de errores de base de datos
app.add_middleware(CustomErrorMiddleware)
app.add_middleware(FrontendRedirectMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes en desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejadores de errores personalizados
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return FileResponse(os.path.join(STATIC_DIR, '404.html'), status_code=404)
    elif exc.status_code == 401:
        return FileResponse(os.path.join(STATIC_DIR, '401.html'), status_code=401)
    elif exc.status_code == 403:
        return FileResponse(os.path.join(STATIC_DIR, '403.html'), status_code=403)
    elif exc.status_code == 500:
        return FileResponse(os.path.join(STATIC_DIR, '500.html'), status_code=500)
    elif exc.status_code == 503:
        return FileResponse(os.path.join(STATIC_DIR, '503.html'), status_code=503)
    elif exc.status_code == 505:
        return FileResponse(os.path.join(STATIC_DIR, '505.html'), status_code=505)
    return JSONResponse(status_code=exc.status_code, content=jsonable_encoder({"detail": exc.detail}))

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=jsonable_encoder({"detail": "Se produjo un error de validación.", "errors": exc.errors()}))

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(url="/loginpage")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Crear todas las tablas en la base de datos
def create_all_tables():
    models_dir = os.path.join(os.path.dirname(__file__), 'db', 'models')
    model_files = [f for f in os.listdir(models_dir) if f.endswith('.py') and f != '__init__.py']
    for model_file in model_files:
        module_name = f"db.models.{model_file[:-3]}"
        importlib.import_module(module_name)
    try:
        create_tables()
    except Exception as e:
        print("Error al crear tablas:", e)
        traceback.print_exc()

# Llamar a la función para crear la base de datos y las tablas
create_database()
create_all_tables()

# Asegurar explícitamente que las tablas de OT se creen
try:
try:
    from ...db.database import create_ot_tables
except ImportError:
    from sql_app.db.database import create_ot_tables
    create_ot_tables()
    print("Tablas de OT creadas explícitamente")
except Exception as e:
    print(f"Error al crear explícitamente tablas de OT: {e}")
    traceback.print_exc()

# Rutas de API Core (no gestionadas dinámicamente)
app.include_router(aut_usuario.router)
app.include_router(usuarios_admin.router)
app.include_router(Generar.router)
app.include_router(configDB.router)
app.include_router(create_admin_router(app))
app.include_router(Blog.router)
app.include_router(Migraciones.router)
app.include_router(Analisis.router)
app.include_router(mail.router)
app.include_router(Scraping.router)
app.include_router(roles_router)
app.include_router(route_ticket.router)

configure_stock_routes(app)

# Crear el gestor de servicios ANTES de importar otros módulos
services_manager = ServicesManager(app)

# Importar y configurar servicio manager
service_manager.initialize_services_manager(services_manager)
app.include_router(service_manager.router)


# Mover esta función antes del startup_event
def ensure_directories():
    """Asegura que existan los directorios necesarios para los servicios y maestros."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    directories = [
        os.path.join(base_dir, "Services"),
        os.path.join(base_dir, "routers", "Maestros")
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            logger.info(f"Creando directorio: {directory}")
            os.makedirs(directory, exist_ok=True)


# Ruta de inicio
@app.get("/index", response_class=HTMLResponse, include_in_schema=False)
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root(request: Request, db: Session = Depends(get_db)):
    blog_posts = db.query(BlogPostModel).order_by(BlogPostModel.created_at.desc()).all()
    return templates.TemplateResponse("index.html", {"request": request, "blog_posts": blog_posts})

# Ruta de términos y condiciones
@app.get("/terminos", response_class=HTMLResponse, include_in_schema=False)
async def get_terminos():
    with open("static/terminos.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read(), status_code=200)
    
# Ruta de privacidad
@app.get("/privacidad", response_class=HTMLResponse, include_in_schema=False)
async def get_privacidad():
    with open("static/privacidad.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read(), status_code=200)

@app.get("/admin", include_in_schema=False)
async def read_admin(current_user: UserDB = Depends(current_user)):
    return {"message": "Tienes acceso a esta ruta", "user": current_user.usuario}