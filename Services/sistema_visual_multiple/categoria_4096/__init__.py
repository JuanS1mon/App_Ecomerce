# ============================================================================
# INIT - CATEGORIA_4096
# ============================================================================
"""
Módulo para categoria_4096
Parte del servicio: sistema_visual_multiple
"""

from .model_categoria_4096 import Categoria4096
from .schema_categoria_4096 import Categoria_4096, Categoria_4096Create, Categoria_4096Update
from .service_categoria_4096 import categoria_4096_service
from .route_categoria_4096 import router

__all__ = [
    "Categoria4096",
    "Categoria_4096",
    "Categoria_4096Create", 
    "Categoria_4096Update",
    "categoria_4096_service",
    "router"
]
