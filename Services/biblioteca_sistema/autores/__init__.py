# ============================================================================
# INIT - AUTORES
# ============================================================================
"""
Módulo para autores
Parte del servicio: biblioteca_sistema
"""

from .model_autores import Autores
from .schema_autores import Autores, AutoresCreate, AutoresUpdate
from .service_autores import autores_service
from .route_autores import router

__all__ = [
    "Autores",
    "Autores",
    "AutoresCreate", 
    "AutoresUpdate",
    "autores_service",
    "router"
]
