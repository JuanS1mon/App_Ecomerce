from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles # que es StaticFiles ?? https://fastapi.tiangolo.com/es/tutorial/static-files/

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from starlette.responses import FileResponse


from routers import modulos
from routers.Contabilidad import Contabilidad
from routers.Articulos import marcas
from routers.Maestros import Usuarios

from prometheus_fastapi_instrumentator import Instrumentator

# Crear una instancia de FastAPI
app = FastAPI()

# Instrumentar la aplicación con Prometheus
Instrumentator().instrument(app).expose(app)


origins = [
    "http://localhost:8000",  # Permitir solicitudes de este origen
    "http://127.0.0.1:8000",  # Permitir solicitudes de este otro origen
    # puedes agregar más orígenes si es necesario
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

#router de la API
app.include_router(marcas.router)
app.include_router(Usuarios.router)
app.include_router(modulos.router)
app.include_router(Contabilidad.router)



app.mount("/static", StaticFiles(directory="static"), name="static")



@app.get("/")
async def read_root():
    return FileResponse('static/login.html')



@app.get("/index")   #EndPoint
async def index():
    return FileResponse('static/index.html')