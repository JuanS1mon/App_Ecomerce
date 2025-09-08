# ============================================================================
# INIT - T
# ============================================================================
"""
Módulo para t
Parte del servicio: test_service
"""

from .model_t import T
from .schema_t import T, TCreate, TUpdate
from .service_t import t_service
from .route_t import router

__all__ = [
    "T",
    "T",
    "TCreate", 
    "TUpdate",
    "t_service",
    "router"
]
