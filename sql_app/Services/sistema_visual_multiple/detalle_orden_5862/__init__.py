# ============================================================================
# INIT - DETALLE_ORDEN_5862
# ============================================================================
"""
Módulo para detalle_orden_5862
Parte del servicio: sistema_visual_multiple
"""

from .model_detalle_orden_5862 import DetalleOrden5862
from .schema_detalle_orden_5862 import Detalle_Orden_5862, Detalle_Orden_5862Create, Detalle_Orden_5862Update
from .service_detalle_orden_5862 import detalle_orden_5862_service
from .route_detalle_orden_5862 import router

__all__ = [
    "DetalleOrden5862",
    "Detalle_Orden_5862",
    "Detalle_Orden_5862Create", 
    "Detalle_Orden_5862Update",
    "detalle_orden_5862_service",
    "router"
]
