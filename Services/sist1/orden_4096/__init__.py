# ============================================================================
# INIT - ORDEN_4096
# ============================================================================
"""
Módulo para orden_4096
Parte del servicio: sist1
"""

from .model_orden_4096 import Orden4096
from .schema_orden_4096 import Orden_4096, Orden_4096Create, Orden_4096Update
from .service_orden_4096 import orden_4096_service
from .route_orden_4096 import router

__all__ = [
    "Orden4096",
    "Orden_4096",
    "Orden_4096Create", 
    "Orden_4096Update",
    "orden_4096_service",
    "router"
]
