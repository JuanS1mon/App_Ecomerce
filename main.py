from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request, status, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.security import OAuth2PasswordRequestForm
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
from pydantic import BaseModel
from datetime import timedelta

# Importa lógica y módulos
from Services.security.security import crear_access_token, authenticate_user, current_user, ACCESS_TOKEN_DURATION
from db.database import Base, engine, get_db, create_database, create_tables
from routers import usuarios as aut_usuario
from routers import Blog
from routers.Maestros import  Route_planilla_test, Route_articulos
from routers.Configuraciones import Generar, configDB, Migraciones,Analisis,Scraping
from Services import mail

from routers.Configuraciones.Admin import create_admin_router

from db.schemas.Maestro.Usuarios import UserDB
from db.models.Blog import BlogPost as BlogPostModel
from sqlalchemy.orm import Session
# Configuración de entorno
load_dotenv()
FRONTEND_URL = os.getenv("FRONTEND_URL")
ORIGINS = os.getenv("ORIGINS", "*").split()

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
        return response

# Agregar middlewares a la app

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes en desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# Rutas de API
app.include_router(aut_usuario.router)
app.include_router(Generar.router)
app.include_router(configDB.router)
app.include_router(create_admin_router(app))
app.include_router(Blog.router)
app.include_router(Migraciones.router)
app.include_router(Analisis.router)
app.include_router(mail.router)
app.include_router(Scraping.router)

# Maestros
app.include_router(Route_planilla_test.router)
app.include_router(Route_articulos.router)

# Manejadores de errores personalizados
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return FileResponse('static/404.html', status_code=404)
    elif exc.status_code == 401:
        return FileResponse('static/401.html', status_code=401)
    return JSONResponse(status_code=exc.status_code, content=jsonable_encoder({"detail": exc.detail}))

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=jsonable_encoder({"detail": "Se produjo un error de validación.", "errors": exc.errors()}))


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
    
    
# Ruta de términos y condiciones
@app.get("/privacidad", response_class=HTMLResponse, include_in_schema=False)
async def get_terminos():
    with open("static/privacidad.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read(), status_code=200)

@app.get("/admin" , include_in_schema=False)
async def read_admin(current_user: UserDB = Depends(current_user)):
    return {"message": "Tienes acceso a esta ruta", "user": current_user.usuario}

