#!/usr/bin/env python3
"""
Servidor simple para probar el Editor Visual
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Editor Visual - Test Server")

# Configurar archivos estáticos
app.mount("/static", StaticFiles(directory="sql_app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
    <head><title>Editor Visual - Test</title></head>
    <body>
        <h1>🎨 Editor Visual - Servidor de Prueba</h1>
        <p><a href="/editor-visual">Abrir Editor Visual</a></p>
        <p><a href="/generar/test">Ir a Fase 2</a></p>
    </body>
    </html>
    """

@app.get("/editor-visual", response_class=HTMLResponse)
@app.get("/editor-visual.html", response_class=HTMLResponse)
async def editor_visual():
    """Editor Visual Avanzado - Fase 3"""
    try:
        with open("sql_app/static/html/editor_visual.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse("""
        <html><body>
        <h1>Editor Visual No Disponible</h1>
        <p>El archivo editor_visual.html no se encontró.</p>
        <a href="/">Volver al inicio</a>
        </body></html>
        """, status_code=404)

@app.get("/generar/test", response_class=HTMLResponse)
async def generador_test():
    """Página de generador para pruebas"""
    try:
        with open("sql_app/static/html/generar.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse("""
        <html><body>
        <h1>Generador No Disponible</h1>
        <p>El archivo generar.html no se encontró.</p>
        <a href="/">Volver al inicio</a>
        </body></html>
        """, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
