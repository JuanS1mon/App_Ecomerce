# ============================================================================
# INIT - ORDEN_2650
# ============================================================================
"""
Módulo para orden_2650
Parte del servicio: dm3
"""

from .model_orden_2650 import Orden2650
from .schema_orden_2650 import Orden_2650, Orden_2650Create, Orden_2650Update
from .service_orden_2650 import orden_2650_service
from .route_orden_2650 import router

__all__ = [
    "Orden2650",
    "Orden_2650",
    "Orden_2650Create", 
    "Orden_2650Update",
    "orden_2650_service",
    "router"
]
