#!/usr/bin/env python3
"""
Servidor simplificado para pruebas - sin emojis que causen problemas de encoding
"""
import sys
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import uvicorn

# Configuración básica
app = FastAPI(title="Test Server", description="Servidor simplificado para pruebas")

# Montar archivos estáticos
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Registrar rutas del proyecto ecomerce
try:
    from Projects.ecomerce.routes_config import configure_routes as configure_ecomerce_routes
    configure_ecomerce_routes(app)
    print("Rutas de ecomerce configuradas correctamente")
except Exception as e:
    print(f"Error configurando rutas de ecomerce: {e}")

@app.get("/")
async def root():
    """Página principal"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Servidor de prueba funcionando</h1>", status_code=200)

if __name__ == "__main__":
    print("Iniciando servidor de prueba...")
    print("Servidor disponible en: http://localhost:8000")
    print("Documentacion API en: http://localhost:8000/docs")

    try:
        uvicorn.run(
            app=app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("Servidor detenido por el usuario")
    except Exception as e:
        print(f"Error al iniciar servidor: {str(e)}")