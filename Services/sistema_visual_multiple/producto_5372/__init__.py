# ============================================================================
# INIT - PRODUCTO_5372
# ============================================================================
"""
Módulo para producto_5372
Parte del servicio: sistema_visual_multiple
"""

from .model_producto_5372 import Producto5372
from .schema_producto_5372 import Producto_5372, Producto_5372Create, Producto_5372Update
from .service_producto_5372 import producto_5372_service
from .route_producto_5372 import router

__all__ = [
    "Producto5372",
    "Producto_5372",
    "Producto_5372Create", 
    "Producto_5372Update",
    "producto_5372_service",
    "router"
]
