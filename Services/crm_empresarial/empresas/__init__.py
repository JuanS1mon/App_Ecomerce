# ============================================================================
# INIT - EMPRESAS
# ============================================================================
"""
Módulo para empresas
Parte del servicio: crm_empresarial
"""

from .model_empresas import Empresas
from .schema_empresas import Empresas, EmpresasCreate, EmpresasUpdate
from .service_empresas import empresas_service
from .route_empresas import router

__all__ = [
    "Empresas",
    "Empresas",
    "EmpresasCreate", 
    "EmpresasUpdate",
    "empresas_service",
    "router"
]
