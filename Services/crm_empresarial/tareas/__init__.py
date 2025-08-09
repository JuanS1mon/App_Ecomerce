# ============================================================================
# INIT - TAREAS
# ============================================================================
"""
Módulo para tareas
Parte del servicio: crm_empresarial
"""

from .model_tareas import Tareas
from .schema_tareas import Tareas, TareasCreate, TareasUpdate
from .service_tareas import tareas_service
from .route_tareas import router

__all__ = [
    "Tareas",
    "Tareas",
    "TareasCreate", 
    "TareasUpdate",
    "tareas_service",
    "router"
]
