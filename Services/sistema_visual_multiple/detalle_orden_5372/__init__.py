# ============================================================================
# INIT - DETALLE_ORDEN_5372
# ============================================================================
"""
Módulo para detalle_orden_5372
Parte del servicio: sistema_visual_multiple
"""

from .model_detalle_orden_5372 import DetalleOrden5372
from .schema_detalle_orden_5372 import Detalle_Orden_5372, Detalle_Orden_5372Create, Detalle_Orden_5372Update
from .service_detalle_orden_5372 import detalle_orden_5372_service
from .route_detalle_orden_5372 import router

__all__ = [
    "DetalleOrden5372",
    "Detalle_Orden_5372",
    "Detalle_Orden_5372Create", 
    "Detalle_Orden_5372Update",
    "detalle_orden_5372_service",
    "router"
]
