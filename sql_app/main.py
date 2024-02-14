from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles # que es StaticFiles ?? https://fastapi.tiangolo.com/es/tutorial/static-files/
from routers import articulos,users,marcas,modulos,Asientos
from fastapi import FastAPI
from errors import register_exception_handlers
from fastapi.middleware.cors import CORSMiddleware

from starlette.responses import FileResponse

app = FastAPI()


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
app.include_router(articulos.router)
app.include_router(users.router)
app.include_router(marcas.router)
app.include_router(modulos.router)
app.include_router(Asientos.router)

register_exception_handlers(app)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse('static/index.html')



@app.get("/nombre")   #EndPoint
async def nombre():
    return { "nombre": "Tecnolar"}