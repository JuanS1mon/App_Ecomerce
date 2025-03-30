import os
from fastapi import APIRouter, status, Depends, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy import text, func
from sqlalchemy.orm import Session
from Services.security.security import get_current_user
from db.database import get_db
from db.models.config.usuarios import usuarios
from datetime import date, timedelta
import json
import logging

# Configurar logger para este módulo
logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="static/html/app_stock")

router = APIRouter(
    include_in_schema=False,  # Oculta todas las rutas de este router en la documentación
    prefix="/app_stock",
    tags=["stock"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

# Función auxiliar para verificar permisos
def verificar_permisos_stock(current_user):
    """Verifica que el usuario tenga permisos para acceder a la gestión de stock"""
    is_authorized = False
    
    if isinstance(current_user, dict):
        if "roles" in current_user:
            is_authorized = any(role["nombre"] in ["admin", "stock_manager"] for role in current_user["roles"])
    else:
        if hasattr(current_user, "roles"):
            is_authorized = any(role.nombre in ["admin", "stock_manager"] for role in current_user.roles)
    
    if not is_authorized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Necesita permisos para acceder a la administración de stock",
            headers={"Location": "/unauthorized"}
        )

@router.get("/pagina")
async def stock_admin_page(request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Verificar permisos
        verificar_permisos_stock(current_user)
        return templates.TemplateResponse("stock_admin.html", {"request": request, "user": current_user})