# ============================================================================
# INIT - PRODUCTO_4096
# ============================================================================
"""
Módulo para producto_4096
Parte del servicio: sist1
"""

from .model_producto_4096 import Producto4096
from .schema_producto_4096 import Producto_4096, Producto_4096Create, Producto_4096Update
from .service_producto_4096 import producto_4096_service
from .route_producto_4096 import router

__all__ = [
    "Producto4096",
    "Producto_4096",
    "Producto_4096Create", 
    "Producto_4096Update",
    "producto_4096_service",
    "router"
]
