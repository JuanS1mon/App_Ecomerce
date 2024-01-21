from fastapi import FastAPI
#from fastapi.staticfiles import StaticFiles # que es StaticFiles ?? https://fastapi.tiangolo.com/es/tutorial/static-files/
from .routers import articulos,users,marcas

app = FastAPI()

#Rutas de la API
app.include_router(articulos.router)
app.include_router(users.router)
app.include_router(marcas.router)



#app.mount("/static", StaticFiles(directory="public"), name="static")



@app.get("/")   #EndPoint
async def root():
    return "hola bienvenido a la API de Tecnolar :)"

@app.get("/nombre")   #EndPoint
async def nombre():
    return { "nombre": "Tecnolar"}
