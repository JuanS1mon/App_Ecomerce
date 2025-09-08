# ============================================================================
# INIT - DETALLE_ORDEN_4096
# ============================================================================
"""
Módulo para detalle_orden_4096
Parte del servicio: sist1
"""

from .model_detalle_orden_4096 import DetalleOrden4096
from .schema_detalle_orden_4096 import Detalle_Orden_4096, Detalle_Orden_4096Create, Detalle_Orden_4096Update
from .service_detalle_orden_4096 import detalle_orden_4096_service
from .route_detalle_orden_4096 import router

__all__ = [
    "DetalleOrden4096",
    "Detalle_Orden_4096",
    "Detalle_Orden_4096Create", 
    "Detalle_Orden_4096Update",
    "detalle_orden_4096_service",
    "router"
]
