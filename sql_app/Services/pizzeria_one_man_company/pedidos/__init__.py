# ============================================================================
# INIT - PEDIDOS
# ============================================================================
"""
Módulo para pedidos
Parte del servicio: pizzeria_one_man_company
"""

from .model_pedidos import Pedidos
from .schema_pedidos import Pedidos, PedidosCreate, PedidosUpdate
from .service_pedidos import pedidos_service
from .route_pedidos import router

__all__ = [
    "Pedidos",
    "Pedidos",
    "PedidosCreate", 
    "PedidosUpdate",
    "pedidos_service",
    "router"
]
