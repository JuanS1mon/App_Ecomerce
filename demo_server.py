# ============================================================================
# SERVIDOR MINIMALISTA PARA PROBAR GENERADOR MULTI-TABLA
# ============================================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

# Importar solo los módulos del generador que necesitamos
from sql_app.routers.config.Generar import router as generar_router

app = FastAPI(title="Generador Multi-Tabla - Demo")

# Configurar archivos estáticos
app.mount("/static", StaticFiles(directory="sql_app/static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="sql_app/static")

# Incluir router del generador
app.include_router(generar_router)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página principal que redirige al generador"""
    return HTMLResponse(content="""
    <html>
        <head><title>Generador Multi-Tabla</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
            <h1>🚀 Generador Multi-Tabla - Demo</h1>
            <p>Sistema de generación de código con soporte para múltiples tablas relacionadas</p>
            <div style="margin: 30px;">
                <a href="/generar/test" style="background: #4f46e5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 10px;">
                    🧪 Generador (Modo Test)
                </a>
                <a href="/generar/multi-table-example" style="background: #059669; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 10px;">
                    📄 Ejemplo JSON
                </a>
            </div>
            <p style="color: #666; margin-top: 30px;">
                ✅ Fase 1 implementada: Soporte para 2+ tablas con relaciones
            </p>
        </body>
    </html>
    """)

if __name__ == "__main__":
    print("🚀 Iniciando servidor demo del generador multi-tabla...")
    print("📍 URL: http://localhost:8001")
    print("🧪 Generador: http://localhost:8001/generar/test")
    print("📄 Ejemplo JSON: http://localhost:8001/generar/multi-table-example")
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)
