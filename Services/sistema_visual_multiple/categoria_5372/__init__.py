# ============================================================================
# INIT - CATEGORIA_5372
# ============================================================================
"""
Módulo para categoria_5372
Parte del servicio: sistema_visual_multiple
"""

from .model_categoria_5372 import Categoria5372
from .schema_categoria_5372 import Categoria_5372, Categoria_5372Create, Categoria_5372Update
from .service_categoria_5372 import categoria_5372_service
from .route_categoria_5372 import router

__all__ = [
    "Categoria5372",
    "Categoria_5372",
    "Categoria_5372Create", 
    "Categoria_5372Update",
    "categoria_5372_service",
    "router"
]
