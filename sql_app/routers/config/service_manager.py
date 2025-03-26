from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, List, Any

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from Services.services_manager import ServicesManager
import os
import logging

# Configuración de logging
logger = logging.getLogger("service_manager")

router = APIRouter(
    prefix="/servicios",
    tags=["servicios"],
    responses={404: {"description": "Not found"}},
)
templates = Jinja2Templates(directory="static/html")

# Variable global para almacenar el gestor de servicios
services_manager = None

def initialize_services_manager(manager: ServicesManager):
    """Inicializa el gestor de servicios global."""
    global services_manager
    services_manager = manager
    logger.info("Gestor de servicios inicializado correctamente")

@router.get("/", response_class=HTMLResponse)
async def get_services_dashboard(request: Request):
    """Página del dashboard de servicios."""
    return templates.TemplateResponse(
        "html/admin/servicios_dashboard.html", 
        {"request": request}
    )

@router.get("/api/listar")
async def list_components():
    """Lista todos los servicios y maestros disponibles (API pública)."""
    if not services_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El gestor de servicios no está inicializado"
        )
    
    return {
        "servicios": services_manager.get_all_services_info(),
        "maestros": services_manager.get_all_maestros_info()
    }

@router.get("/listar")
async def list_components_admin():
    """Lista todos los servicios y maestros disponibles (acceso público)."""
    if not services_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El gestor de servicios no está inicializado"
        )
    
    return {
        "servicios": services_manager.get_all_services_info(),
        "maestros": services_manager.get_all_maestros_info()
    }

@router.post("/servicios/{service_id}/activar")
async def activate_service(service_id: str):
    """Activa un servicio específico."""
    if not services_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El gestor de servicios no está inicializado"
        )
    
    success = services_manager.register_service(service_id)
    if success:
        return {"status": "success", "message": f"Servicio {service_id} activado correctamente"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pudo activar el servicio {service_id}"
        )

@router.post("/servicios/{service_id}/desactivar")
async def deactivate_service(service_id: str):
    """Desactiva un servicio específico."""
    if not services_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El gestor de servicios no está inicializado"
        )
    
    success = services_manager.unregister_service(service_id)
    if success:
        return {"status": "success", "message": f"Servicio {service_id} desactivado correctamente"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pudo desactivar el servicio {service_id}"
        )

@router.post("/maestros/{maestro_id}/activar")
async def activate_maestro(maestro_id: str):
    """Activa un maestro específico."""
    if not services_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El gestor de servicios no está inicializado"
        )
    
    success = services_manager.register_maestro(maestro_id)
    if success:
        return {"status": "success", "message": f"Maestro {maestro_id} activado correctamente"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pudo activar el maestro {maestro_id}"
        )

@router.post("/maestros/{maestro_id}/desactivar")
async def deactivate_maestro(maestro_id: str):
    """Desactiva un maestro específico."""
    if not services_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El gestor de servicios no está inicializado"
        )
    
    success = services_manager.unregister_maestro(maestro_id)
    if success:
        return {"status": "success", "message": f"Maestro {maestro_id} desactivado correctamente"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pudo desactivar el maestro {maestro_id}"
        )

@router.post("/refrescar")
async def refresh_all():
    """Refresca todos los servicios y maestros."""
    if not services_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El gestor de servicios no está inicializado"
        )
    
    services_results = services_manager.register_all_services()
    maestros_results = services_manager.register_all_maestros()
    
    return {
        "servicios": services_results,
        "maestros": maestros_results
    }