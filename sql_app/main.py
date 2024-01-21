from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles # que es StaticFiles ?? https://fastapi.tiangolo.com/es/tutorial/static-files/
from routers import articulos,users,marcas

from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse

from db.schemas.modulos import Modulos
from db.database import  get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from db.crud.modulos import gets
from starlette.responses import FileResponse

app = FastAPI()

#router de la API
app.include_router(articulos.router)
app.include_router(users.router)
app.include_router(marcas.router)


app.mount("/static", StaticFiles(directory="static"), name="static")


# Rutas de la API
@app.get("/modulos", response_model=list[Modulos])   #EndPoint
async def get_modulos(db: Session = Depends(get_db)):
    modulos = gets(db)
    return modulos


@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

@app.get("/nombre")   #EndPoint
async def nombre():
    return { "nombre": "Tecnolar"}