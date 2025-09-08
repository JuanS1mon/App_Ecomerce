# ============================================================================
# INIT - TABLA1
# ============================================================================
"""
Módulo para tabla1
Parte del servicio: mi_sistema
"""

from .model_tabla1 import Tabla1
from .schema_tabla1 import Tabla1, Tabla1Create, Tabla1Update
from .service_tabla1 import tabla1_service
from .route_tabla1 import router

__all__ = [
    "Tabla1",
    "Tabla1",
    "Tabla1Create", 
    "Tabla1Update",
    "tabla1_service",
    "router"
]
