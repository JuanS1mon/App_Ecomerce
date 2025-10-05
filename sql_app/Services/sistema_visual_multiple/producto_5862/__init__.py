# ============================================================================
# INIT - PRODUCTO_5862
# ============================================================================
"""
Módulo para producto_5862
Parte del servicio: sistema_visual_multiple
"""

from .model_producto_5862 import Producto5862
from .schema_producto_5862 import Producto_5862, Producto_5862Create, Producto_5862Update
from .service_producto_5862 import producto_5862_service
from .route_producto_5862 import router

__all__ = [
    "Producto5862",
    "Producto_5862",
    "Producto_5862Create", 
    "Producto_5862Update",
    "producto_5862_service",
    "router"
]
