from fastapi import Depends, FastAPI, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles # que es StaticFiles ?? https://fastapi.tiangolo.com/es/tutorial/static-files/
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from fastapi.templating import Jinja2Templates

from requests import Session


from fastapi.middleware.cors import CORSMiddleware

from starlette.responses import FileResponse
from datetime import timedelta

from Services.security.security import crear_access_token, authenticate_user, current_user, ACCESS_TOKEN_DURATION
from db.database import get_db
from pydantic import BaseModel


from routers import usuarios as aut_usuario
from routers import Blog
from routers.Maestros import  Route_usuario, Route_Companias, Route_Productos, Route_Usuarios_roles, Route_transactiones, Route_inventarios
from routers.Configuraciones import Generar,Admin,configDB
from routers.Configuraciones.Admin import create_admin_router,create_admin_router

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError

from db.schemas.Maestro.Usuarios import UserDB
from pydantic import BaseModel



from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
#from prometheus_fastapi_instrumentator import Instrumentator

#habilitar prometheus  para tener un monitoreo de la aplicacion
#cd

#atomatizar la creacion de dashboards
#automatizar subir y bajar de git
#automatizar la creación de la documentación
#usar nssm para crear un servicio de windows
#usar docker para crear un contenedor

#Modelos
# Crear todas las tablas de la base de datos
from db.database import Base, engine  # Importa engine desde db.database
#from db.models import * # Importa los modelos desde db.models
import traceback
import os
import importlib

#Ruta de la carpeta models
models_dir = os.path.join(os.path.dirname(__file__), 'db', 'models')

# Listar todos los archivos en la carpeta models
model_files = [f for f in os.listdir(models_dir) if f.endswith('.py') and f != '__init__.py']

# Importar dinámicamente todos los módulos en la carpeta models
for model_file in model_files:
    module_name = f"db.models.{model_file[:-3]}"  # Eliminar la extensión .py
    importlib.import_module(module_name)
# Crear todas las tablas de la base de datos
try:
    Base.metadata.create_all(bind=engine)
    print("Tablas conocidas por SQLAlchemy:", Base.metadata.tables)
except Exception as e:
    print("Ha ocurrido un error:", e)
    traceback.print_exc()


# Crear una instancia de FastAPI
app = FastAPI()

# Instrumentar la aplicación con Prometheus
#Instrumentator().instrument(app).expose(app)


origins = [
    "http://localhost",  # Permitir solicitudes desde localhost
    "http://localhost:8000",  # Permitir solicitudes desde localhost con puerto 8000
    "https://example.com",  # Permitir solicitudes desde example.com
    # Puedes agregar más orígenes si es necesario
]

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:8000"],  # Agrega los orígenes necesarios
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],  # Permitir todos los encabezados
)




#Configuraciones.
#Inicio Router de la API
app.include_router(aut_usuario.router)
app.include_router(Generar.router)
app.include_router(configDB.router)
app.include_router(create_admin_router(app))
app.include_router(Blog.router)

#Maestros
app.include_router(Route_inventarios.router)
app.include_router(Route_transactiones.router)
app.include_router(Route_Usuarios_roles.router)
app.include_router(Route_Productos.router)
app.include_router(Route_Companias.router)
app.include_router(Route_usuario.router)



#Fin Router de la API

templates = Jinja2Templates(directory="static")


# Ruta para servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")


# Ruta para login
# Ruta para la página de inicio
@app.get("/index", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Dashboard
class Item(BaseModel):
    name: str
    value: int

@app.get("/dashboard_data")
async def get_dashboard_data():
    # Aquí es donde obtendrías los datos reales para tu dashboard.
    # Por ahora, solo devolveré algunos datos de ejemplo.
    return [
        Item(name="Item 1", value=123),
        Item(name="Item 2", value=456),
        Item(name="Item 3", value=789),
    ]

@app.get("/admin")
async def read_admin(current_user: UserDB = Depends(current_user)):
    return {"message": "Tienes acceso a esta ruta", "user": current_user.usuario}

# Manejador de excepciones para errores de validación
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": "Se produjo un error de validación.", "errors": exc.errors()}),
    )

class NotFoundMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if response.status_code == 404:
            return FileResponse('static/404.html', status_code=404)
        return response

class UnauthorizedMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if response.status_code == 401:
            return FileResponse('static/401.html', status_code=401)
        return response

# Añadir los middlewares a la aplicación
app.add_middleware(NotFoundMiddleware)
app.add_middleware(UnauthorizedMiddleware)

# Manejador de excepciones para errores HTTP
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return FileResponse('static/404.html', status_code=404)
    elif exc.status_code == 401:
        return FileResponse('static/401.html', status_code=401)
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder({"detail": exc.detail}),
    )