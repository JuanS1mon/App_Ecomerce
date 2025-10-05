# ============================================================================
# INIT - CATEGORIA_5862
# ============================================================================
"""
Módulo para categoria_5862
Parte del servicio: sistema_visual_multiple
"""

from .model_categoria_5862 import Categoria5862
from .schema_categoria_5862 import Categoria_5862, Categoria_5862Create, Categoria_5862Update
from .service_categoria_5862 import categoria_5862_service
from .route_categoria_5862 import router

__all__ = [
    "Categoria5862",
    "Categoria_5862",
    "Categoria_5862Create", 
    "Categoria_5862Update",
    "categoria_5862_service",
    "router"
]
