# ============================================================================
# INIT - PRODUCTOS
# ============================================================================
"""
Módulo para productos
Parte del servicio: pizzeria_one_man_company
"""

from .model_productos import Productos
from .schema_productos import Productos, ProductosCreate, ProductosUpdate
from .service_productos import productos_service
from .route_productos import router

__all__ = [
    "Productos",
    "Productos",
    "ProductosCreate", 
    "ProductosUpdate",
    "productos_service",
    "router"
]
