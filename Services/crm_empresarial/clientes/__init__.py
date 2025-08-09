# ============================================================================
# INIT - CLIENTES
# ============================================================================
"""
Módulo para clientes
Parte del servicio: crm_empresarial
"""

from .model_clientes import Clientes
from .schema_clientes import Clientes, ClientesCreate, ClientesUpdate
from .service_clientes import clientes_service
from .route_clientes import router

__all__ = [
    "Clientes",
    "Clientes",
    "ClientesCreate", 
    "ClientesUpdate",
    "clientes_service",
    "router"
]
