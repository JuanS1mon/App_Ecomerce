"""
Router simple para servir la página de administración de mensajes
"""

from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter(
    prefix="/administracion",
    tags=["admin-simple"],
    responses={404: {"description": "Not found"}},
)

@router.get("/mensajes")
async def admin_mensajes_page():
    """
    Servir la página de administración de mensajes desde Services
    """
    # Nueva ruta del archivo HTML en Services
    html_file = os.path.join("sql_app", "Services", "mensajes", "frontend", "admin", "mensajes.html")
    
    if os.path.exists(html_file):
        return FileResponse(html_file, media_type="text/html")
    else:
        return {"error": "Página no encontrada", "file": html_file}

@router.get("/mensajes-demo")
async def admin_mensajes_demo_page():
    """
    Servir la página demo de administración de mensajes desde Services
    """
    # Nueva ruta del archivo HTML demo en Services
    html_file = os.path.join("sql_app", "Services", "mensajes", "frontend", "admin", "mensajes-demo.html")
    
    if os.path.exists(html_file):
        return FileResponse(html_file, media_type="text/html")
    else:
        return {"error": "Página demo no encontrada", "file": html_file}

@router.get("/test")
async def test_admin_simple():
    """
    Endpoint de prueba
    """
    return {
        "mensaje": "Router simple de administración funcionando",
        "url": "/administracion/mensajes"
    }
