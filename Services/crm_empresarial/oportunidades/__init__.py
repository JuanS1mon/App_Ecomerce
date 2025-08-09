# ============================================================================
# INIT - OPORTUNIDADES
# ============================================================================
"""
Módulo para oportunidades
Parte del servicio: crm_empresarial
"""

from .model_oportunidades import Oportunidades
from .schema_oportunidades import Oportunidades, OportunidadesCreate, OportunidadesUpdate
from .service_oportunidades import oportunidades_service
from .route_oportunidades import router

__all__ = [
    "Oportunidades",
    "Oportunidades",
    "OportunidadesCreate", 
    "OportunidadesUpdate",
    "oportunidades_service",
    "router"
]
