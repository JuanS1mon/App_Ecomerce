#!/usr/bin/env python3
"""Versión simplificada del generador para debugging"""

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import logging
import os

# Configurar router básico
router = APIRouter(
    include_in_schema=False,
    prefix="/generar",
    tags=["generar"]
)

# Configurar templates
templates = Jinja2Templates(directory="sql_app/static")

# Logger básico
logger = logging.getLogger("generador_simple")

@router.get("/")
async def migraciones_page(request: Request):
    """Endpoint principal del generador (versión simplificada)"""
    try:
        logger.info("🚀 Acceso al generador simplificado")
        
        # Datos de usuario mock
        mock_user_data = {
            "user": {"username": "generator_user", "email": "generator@example.com"},
            "user_count": 1,
            "activities": [],
            "is_admin": True,
            "is_authenticated": True
        }
        
        # Verificar template
        template_path = "sql_app/static/html/generar.html"
        if os.path.exists(template_path):
            logger.info(f"✅ Template encontrado: {template_path}")
            return templates.TemplateResponse("html/generar.html", {
                "request": request, 
                **mock_user_data
            })
        else:
            logger.error(f"❌ Template no encontrado: {template_path}")
            return HTMLResponse(content="""
            <html>
                <head><title>Generador de Aplicaciones</title></head>
                <body>
                    <h1>🛠️ Generador de Aplicaciones</h1>
                    <p>Template no encontrado: sql_app/static/html/generar.html</p>
                </body>
            </html>
            """, status_code=200)
            
    except Exception as e:
        logger.error(f"❌ Error en generador: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return HTMLResponse(content=f"""
        <html>
            <head><title>Error en Generador</title></head>
            <body>
                <h1>Error en Generador</h1>
                <p>Error: {str(e)}</p>
                <pre>{traceback.format_exc()}</pre>
            </body>
        </html>
        """, status_code=500)

@router.post("/generate")
async def generate_simple(request: Request):
    """Endpoint simplificado para generación"""
    try:
        json_data = await request.json()
        logger.info(f"📝 Solicitud de generación: {json_data.get('module_name', 'sin nombre')}")
        
        return {
            "success": True,
            "message": "✅ Generador simplificado funcionando. Los endpoints complejos están en desarrollo.",
            "received_data": json_data
        }
        
    except Exception as e:
        logger.error(f"❌ Error en generación: {str(e)}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }

if __name__ == "__main__":
    print("✅ Generador simplificado cargado correctamente")