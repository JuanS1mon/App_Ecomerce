# ============================================================================
# INIT - CATEGORIA_2650
# ============================================================================
"""
Módulo para categoria_2650
Parte del servicio: dm3
"""

from .model_categoria_2650 import Categoria2650
from .schema_categoria_2650 import Categoria_2650, Categoria_2650Create, Categoria_2650Update
from .service_categoria_2650 import categoria_2650_service
from .route_categoria_2650 import router

__all__ = [
    "Categoria2650",
    "Categoria_2650",
    "Categoria_2650Create", 
    "Categoria_2650Update",
    "categoria_2650_service",
    "router"
]
