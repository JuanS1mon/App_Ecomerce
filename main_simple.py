#!/usr/bin/env python3
"""
Servidor main simplificado para que funcione el Editor Visual
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sql_app.routers import frontend_pages
import os

app = FastAPI(title="Sistema de Stock - Simplificado")

# Incluir rutas de frontend
app.include_router(frontend_pages.router)

# Configurar archivos estáticos
app.mount("/static", StaticFiles(directory="sql_app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse("""
    <html>
    <head>
        <title>Sistema de Stock</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>🎨 Sistema de Stock - Editor Visual</h1>
        <div style="margin: 20px;">
            <h2>Accesos disponibles:</h2>
            <ul>
                <li><a href="/editor-visual">Editor Visual Avanzado</a></li>
                <li><a href="/generar/test">Generador Fase 2</a></li>
            </ul>
        </div>
    </body>
    </html>
    """)

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
    uvicorn.run(app, host="127.0.0.1", port=8002)
