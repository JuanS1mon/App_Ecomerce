"""
Router para servir archivos estáticos del módulo de mensajes
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter(
    prefix="/mensajes/static",
    tags=["mensajes-static"],
    responses={404: {"description": "Not found"}},
)

@router.get("/admin/{file_path:path}")
async def servir_archivos_admin(file_path: str):
    """
    Servir archivos estáticos del admin de mensajes (JS, CSS, etc.)
    """
    # Ruta base para archivos estáticos de admin de mensajes
    base_path = os.path.join("sql_app", "Services", "mensajes", "frontend", "admin")
    file_full_path = os.path.join(base_path, file_path)
    
    if not os.path.exists(file_full_path):
        raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {file_path}")
    
    # Determinar el tipo de contenido basado en la extensión
    if file_path.endswith('.js'):
        media_type = "application/javascript"
    elif file_path.endswith('.css'):
        media_type = "text/css"
    elif file_path.endswith('.html'):
        media_type = "text/html"
    elif file_path.endswith('.json'):
        media_type = "application/json"
    else:
        media_type = "text/plain"
    
    return FileResponse(file_full_path, media_type=media_type)

@router.get("/js/{file_name}")
async def servir_javascript(file_name: str):
    """
    Servir archivos JavaScript específicamente
    """
    # Buscar primero en el directorio static/js
    js_path_static = os.path.join("sql_app", "Services", "mensajes", "static", "js", file_name)
    
    if os.path.exists(js_path_static):
        return FileResponse(js_path_static, media_type="application/javascript")
    
    # Si no existe, buscar en frontend/admin/js
    js_path = os.path.join("sql_app", "Services", "mensajes", "frontend", "admin", "js", file_name)
    
    if not os.path.exists(js_path):
        raise HTTPException(status_code=404, detail=f"Archivo JS no encontrado: {file_name}")
    
    return FileResponse(js_path, media_type="application/javascript")
