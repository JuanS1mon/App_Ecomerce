# ============================================================================
# INIT - PRODUCTO_2650
# ============================================================================
"""
Módulo para producto_2650
Parte del servicio: dm3
"""

from .model_producto_2650 import Producto2650
from .schema_producto_2650 import Producto_2650, Producto_2650Create, Producto_2650Update
from .service_producto_2650 import producto_2650_service
from .route_producto_2650 import router

__all__ = [
    "Producto2650",
    "Producto_2650",
    "Producto_2650Create", 
    "Producto_2650Update",
    "producto_2650_service",
    "router"
]
