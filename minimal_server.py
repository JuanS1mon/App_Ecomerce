from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

app = FastAPI()

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return HTMLResponse("<h1>Servidor funcionando</h1>")

@app.get("/test_counter")
async def test_counter():
    # Leer el archivo HTML de prueba del contador
    html_file = os.path.join(os.getcwd(), "test_cart_counter.html")
    if os.path.exists(html_file):
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content)
    else:
        return HTMLResponse("<h1>Archivo de prueba no encontrado</h1>")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8003)