# ============================================================================
# INIT - CONTACTOS
# ============================================================================
"""
Módulo para contactos
Parte del servicio: crm_empresarial
"""

from .model_contactos import Contactos
from .schema_contactos import Contactos, ContactosCreate, ContactosUpdate
from .service_contactos import contactos_service
from .route_contactos import router

__all__ = [
    "Contactos",
    "Contactos",
    "ContactosCreate", 
    "ContactosUpdate",
    "contactos_service",
    "router"
]
