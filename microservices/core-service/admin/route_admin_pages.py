"""
Router para servir las páginas de administración
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
import os

from ...db.database import get_db
from ...Services.security.security import get_current_user
from db.models.config.usuarios import Usuarios

router = APIRouter(
    prefix="/admin",
    tags=["admin-pages"],
    responses={404: {"description": "Not found"}},
)

@router.get("/mensajes", response_class=HTMLResponse)
async def admin_mensajes_page(request: Request):
    """
    Servir la página de administración de mensajes
    """
    # Ruta del archivo HTML
    html_file = os.path.join("sql_app", "static", "admin", "mensajes.html")
    
    if os.path.exists(html_file):
        return FileResponse(html_file, media_type="text/html")
    else:
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head><title>Página No Encontrada</title></head>
            <body>
                <h1>Página de Administración en Desarrollo</h1>
                <p>La página de administración de mensajes está siendo desarrollada.</p>
                <a href="/">Volver al Inicio</a>
            </body>
            </html>
            """,
            status_code=404
        )

@router.get("/test-admin")
async def test_admin_page():
    """
    Endpoint de prueba para verificar el router de páginas de admin
    """
    return {
        "mensaje": "Router de páginas de administración funcionando",
        "endpoints": [
            "/admin/mensajes - Página de administración de mensajes"
        ]
    }
