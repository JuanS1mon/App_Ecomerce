# ============================================================================
# INIT - DETALLE_ORDEN_7306
# ============================================================================
"""
Módulo para detalle_orden_7306
Parte del servicio: sistema_visual_multiple
"""

from .model_detalle_orden_7306 import DetalleOrden7306
from .schema_detalle_orden_7306 import Detalle_Orden_7306, Detalle_Orden_7306Create, Detalle_Orden_7306Update
from .service_detalle_orden_7306 import detalle_orden_7306_service
from .route_detalle_orden_7306 import router

__all__ = [
    "DetalleOrden7306",
    "Detalle_Orden_7306",
    "Detalle_Orden_7306Create", 
    "Detalle_Orden_7306Update",
    "detalle_orden_7306_service",
    "router"
]
