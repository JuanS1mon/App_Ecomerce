# ============================================================================
# INIT - LIBROS
# ============================================================================
"""
Módulo para libros
Parte del servicio: biblioteca_sistema
"""

from .model_libros import Libros
from .schema_libros import Libros, LibrosCreate, LibrosUpdate
from .service_libros import libros_service
from .route_libros import router

__all__ = [
    "Libros",
    "Libros",
    "LibrosCreate", 
    "LibrosUpdate",
    "libros_service",
    "router"
]
