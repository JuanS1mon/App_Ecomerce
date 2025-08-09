# ============================================================================
# INIT - DETALLE_ORDEN
# ============================================================================
"""
Módulo para detalle_orden
Parte del servicio: ecommerce_app
"""

from .model_detalle_orden import DetalleOrden
from .schema_detalle_orden import Detalle_Orden, Detalle_OrdenCreate, Detalle_OrdenUpdate
from .service_detalle_orden import detalle_orden_service
from .route_detalle_orden import router

__all__ = [
    "DetalleOrden",
    "Detalle_Orden",
    "Detalle_OrdenCreate", 
    "Detalle_OrdenUpdate",
    "detalle_orden_service",
    "router"
]
