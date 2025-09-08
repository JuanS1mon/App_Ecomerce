# ============================================================================
# INIT - USUARIO_2650
# ============================================================================
"""
Módulo para usuario_2650
Parte del servicio: dm3
"""

from .model_usuario_2650 import Usuario2650
from .schema_usuario_2650 import Usuario_2650, Usuario_2650Create, Usuario_2650Update
from .service_usuario_2650 import usuario_2650_service
from .route_usuario_2650 import router

__all__ = [
    "Usuario2650",
    "Usuario_2650",
    "Usuario_2650Create", 
    "Usuario_2650Update",
    "usuario_2650_service",
    "router"
]
