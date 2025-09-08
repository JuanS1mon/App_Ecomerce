# ============================================================================
# INIT - DETALLE_ORDEN_2650
# ============================================================================
"""
Módulo para detalle_orden_2650
Parte del servicio: dm3
"""

from .model_detalle_orden_2650 import DetalleOrden2650
from .schema_detalle_orden_2650 import Detalle_Orden_2650, Detalle_Orden_2650Create, Detalle_Orden_2650Update
from .service_detalle_orden_2650 import detalle_orden_2650_service
from .route_detalle_orden_2650 import router

__all__ = [
    "DetalleOrden2650",
    "Detalle_Orden_2650",
    "Detalle_Orden_2650Create", 
    "Detalle_Orden_2650Update",
    "detalle_orden_2650_service",
    "router"
]
