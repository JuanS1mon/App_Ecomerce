from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from typing import Dict, List, Any, Optional
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from Services.services_manager import ServicesManager
import os
import logging
import traceback
from pydantic import BaseModel
import importlib
import importlib.util
import sys


# Configuración de logging
logger = logging.getLogger("service_manager")

# Modelo para respuestas estándar
class ServiceResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict] = None

router = APIRouter(
    prefix="/servicios",
    tags=["servicios"],
    responses={
        404: {"model": ServiceResponse, "description": "Componente no encontrado"},
        500: {"model": ServiceResponse, "description": "Error interno del servidor"}
    },
)
templates = Jinja2Templates(directory="static/html")



# Añade esta variable global al principio del archivo
services_manager = None

# Añadir este método a la clase ServicesManager:

def activate_saved_services(self):
    """Activa todos los servicios que estaban marcados como activos en el estado guardado."""
    activated_services = 0
    activated_maestros = 0
    
    # Activar servicios guardados
    for service_id, is_active in list(self.active_services.items()):
        if is_active:
            try:
                # Intentamos registrar el servicio (lo que lo activa realmente)
                if self.register_service(service_id):
                    activated_services += 1
            except Exception as e:
                logger.error(f"Error al activar servicio guardado {service_id}: {str(e)}")
    
    # Activar maestros guardados
    for maestro_id, is_active in list(self.active_maestros.items()):
        if is_active:
            try:
                if self.register_maestro(maestro_id):
                    activated_maestros += 1
            except Exception as e:
                logger.error(f"Error al activar maestro guardado {maestro_id}: {str(e)}")
    
    logger.info(f"Activados {activated_services} servicios y {activated_maestros} maestros según el estado guardado")
    return activated_services + activated_maestros > 0
# Añade esta función para inicializar el gestor de servicios
def initialize_services_manager(manager):
    """Inicializa el gestor de servicios y carga todos los modelos automáticamente."""
    global services_manager
    services_manager = manager
    
    # Importar todos los modelos de servicios
    import_service_models()
    
    # Crear tablas después de importar todos los modelos
    from db.database import Base, engine
    Base.metadata.create_all(bind=engine)
    
    logger.info("Gestor de servicios inicializado correctamente")
    
    return services_manager

def import_service_models():
    """Importa automáticamente todos los modelos de servicios."""
    if not services_manager:
        logger.warning("El gestor de servicios no está inicializado")
        return
        
    base_dir = services_manager.base_dir
    services_dir = os.path.join(base_dir, "Services")
    
    if not os.path.exists(services_dir):
        logger.warning(f"El directorio de servicios {services_dir} no existe")
        return
    
    # Recorrer todos los directorios de servicios
    for service_name in os.listdir(services_dir):
        service_path = os.path.join(services_dir, service_name)
        
        # Omitir archivos y directorios especiales
        if not os.path.isdir(service_path) or service_name.startswith('__'):
            continue
            
        # Buscar archivos model_*.py en cada directorio de servicio
        for filename in os.listdir(service_path):
            if filename.startswith('model_') and filename.endswith('.py'):
                module_path = f"Services.{service_name}.{filename[:-3]}"
                
                try:
                    logger.info(f"Importando modelo: {module_path}")
                    
                    if module_path in sys.modules:
                        importlib.reload(sys.modules[module_path])
                    else:
                        importlib.import_module(module_path)
                        
                    logger.info(f"Modelo {module_path} importado correctamente")
                except Exception as e:
                    logger.error(f"Error al importar modelo {module_path}: {str(e)}")

def get_services_manager():
    """Helper para obtener el gestor de servicios con verificación."""
    if not services_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El gestor de servicios no está inicializado"
        )
    return services_manager

@router.get("/", response_class=HTMLResponse)
async def get_services_dashboard(request: Request):
    """Página del dashboard de servicios."""
    return templates.TemplateResponse(
        "service_manager.html", 
        {"request": request}
    )

@router.get("/api/listar")
async def list_components():
    """Lista todos los servicios y maestros disponibles (API pública)."""
    manager = get_services_manager()
    
    try:
        return {
            "servicios": manager.get_all_services_info(),
            "maestros": manager.get_all_maestros_info()
        }
    except Exception as e:
        logger.error(f"Error al listar componentes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar componentes: {str(e)}"
        )

@router.get("/listar")
async def list_components_admin():
    """Lista todos los servicios y maestros disponibles (acceso público)."""
    manager = get_services_manager()
    
    try:
        # Forzar un nuevo escaneo para detectar nuevos servicios
        services = manager.scan_services()
        maestros = manager.scan_maestros() if hasattr(manager, 'scan_maestros') else []
        
        return {
            "servicios": manager.get_all_services_info(),
            "maestros": manager.get_all_maestros_info(),
            "nuevos_servicios": services,
            "nuevos_maestros": maestros
        }
    except Exception as e:
        logger.error(f"Error al listar componentes: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar componentes: {str(e)}"
        )

@router.post("/{service_id}/activar", response_model=ServiceResponse)
async def activate_service(service_id: str, background_tasks: BackgroundTasks):
    """Activa un servicio específico."""
    manager = get_services_manager()
    
    try:
        # Activar en segundo plano para no bloquear la respuesta
        def activate():
            try:
                success = manager.register_service(service_id)
                logger.info(f"Servicio {service_id} {'activado' if success else 'no se pudo activar'}")
            except Exception as e:
                logger.error(f"Error al activar servicio {service_id}: {str(e)}")
                
        background_tasks.add_task(activate)
        
        # Marcar como activo en la configuración
        manager.active_services[service_id] = True
        manager.save_state()
        
        return ServiceResponse(
            status="success",
            message=f"Servicio {service_id} marcado para activación"
        )
    except Exception as e:
        logger.error(f"Error al activar servicio {service_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al activar servicio: {str(e)}"
        )

@router.post("/{service_id}/refrescar", response_model=ServiceResponse)
async def refresh_service(service_id: str, background_tasks: BackgroundTasks):
    """Refresca un servicio específico."""
    manager = get_services_manager()
    
    try:
        # Siempre forzar el refresco, incluso si está marcado como activo
        # Intentar desactivar primero si está activo en el estado
        if service_id in manager.active_services and manager.active_services[service_id]:
            manager.unregister_service(service_id)
        
        # Luego volver a cargarlo desde cero
        router = manager.load_service(service_id)
        if router:
            manager.app.include_router(router)
            manager.active_services[service_id] = True
            manager.save_state()
            success = True
        else:
            success = False
        
        if not success:
            return ServiceResponse(
                status="error",
                message=f"No se pudo refrescar el servicio {service_id}"
            )
        
        return ServiceResponse(
            status="success", 
            message=f"Servicio {service_id} refrescado correctamente"
        )
    except Exception as e:
        logger.error(f"Error al refrescar servicio {service_id}: {str(e)}")
        return ServiceResponse(
            status="error",
            message=f"Error al refrescar servicio: {str(e)}"
        )

@router.post("/{service_id}/desactivar", response_model=ServiceResponse)
async def deactivate_service(service_id: str, background_tasks: BackgroundTasks):
    """Desactiva un servicio específico."""
    manager = get_services_manager()
    
    try:
        # Desactivar en segundo plano
        def deactivate():
            try:
                success = manager.unregister_service(service_id)
                logger.info(f"Servicio {service_id} {'desactivado' if success else 'no se pudo desactivar'}")
            except Exception as e:
                logger.error(f"Error al desactivar servicio {service_id}: {str(e)}")
        
        background_tasks.add_task(deactivate)
        
        # Marcar como inactivo en la configuración
        manager.active_services[service_id] = False
        manager.save_state()
        
        return ServiceResponse(
            status="success",
            message=f"Servicio {service_id} marcado para desactivación"
        )
    except Exception as e:
        logger.error(f"Error al desactivar servicio {service_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al desactivar servicio: {str(e)}"
        )

@router.post("/maestros/{maestro_id}/activar", response_model=ServiceResponse)
async def activate_maestro(maestro_id: str):
    """Activa un maestro específico."""
    manager = get_services_manager()
    
    try:
        success = manager.register_maestro(maestro_id)
        
        if success:
            manager.active_maestros[maestro_id] = True
            manager.save_state()
            return ServiceResponse(
                status="success",
                message=f"Maestro {maestro_id} activado correctamente"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se pudo activar el maestro {maestro_id}"
            )
    except Exception as e:
        logger.error(f"Error al activar maestro {maestro_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al activar maestro: {str(e)}"
        )

@router.post("/maestros/{maestro_id}/desactivar", response_model=ServiceResponse)
async def deactivate_maestro(maestro_id: str):
    """Desactiva un maestro específico."""
    manager = get_services_manager()
    
    try:
        success = manager.unregister_maestro(maestro_id)
        
        if success:
            manager.active_maestros[maestro_id] = False
            manager.save_state()
            return ServiceResponse(
                status="success",
                message=f"Maestro {maestro_id} desactivado correctamente"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se pudo desactivar el maestro {maestro_id}"
            )
    except Exception as e:
        logger.error(f"Error al desactivar maestro {maestro_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al desactivar maestro: {str(e)}"
        )

@router.post("/refrescar", response_model=ServiceResponse)
async def refresh_all():
    """Refresca todos los servicios y maestros activos."""
    manager = get_services_manager()
    
    try:
        services_results = manager.register_all_services()
        maestros_results = manager.register_all_maestros()
        
        return ServiceResponse(
            status="success",
            message="Todos los servicios y maestros activos han sido refrescados",
            data={
                "servicios": services_results,
                "maestros": maestros_results
            }
        )
    except Exception as e:
        logger.error(f"Error al refrescar servicios y maestros: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al refrescar servicios y maestros: {str(e)}"
        )

@router.post("/escanear", response_model=ServiceResponse)
async def scan_components():
    """Escanea en busca de nuevos servicios y maestros sin activarlos."""
    manager = get_services_manager()
    
    try:
        services = manager.scan_services()
        maestros = manager.scan_maestros() if hasattr(manager, 'scan_maestros') else []
        
        return ServiceResponse(
            status="success",
            message="Escaneo de servicios y maestros completado",
            data={
                "servicios": services,
                "maestros": maestros
            }
        )
    except Exception as e:
        logger.error(f"Error al escanear componentes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al escanear componentes: {str(e)}"
        )