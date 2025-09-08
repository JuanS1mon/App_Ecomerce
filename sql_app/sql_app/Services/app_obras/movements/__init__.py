"""
Módulo de Movimientos de Obras de Arte

Este módulo maneja el tracking y registro de todos los movimientos de obras de arte
incluyendo préstamos, ventas, cesiones, traslados y exhibiciones.

Componentes:
- model_movements: Modelo de datos para movimientos
- model_contacts: Modelo de datos para contactos
- schema_movements: Schemas de validación para APIs
- service_movements: Lógica de negocio y CRUD
- route_movements: Endpoints de la API
- movement_integrations: Funciones de integración automática
"""

from .model_movements import Movements, MovementType, MovementStatus
from .model_contacts import Contacts
from .schema_movements import (
    MovementCreate, MovementUpdate, MovementResponse,
    ContactCreate, ContactUpdate, ContactResponse,
    GroupedMovementCreate, MovementHistoryResponse
)
from .service_movements import MovementService, ContactService
from .movement_integrations import create_sale_movement, create_exhibition_movement

__all__ = [
    # Models
    "Movements", "MovementType", "MovementStatus", "Contacts",
    
    # Schemas
    "MovementCreate", "MovementUpdate", "MovementResponse",
    "ContactCreate", "ContactUpdate", "ContactResponse",
    "GroupedMovementCreate", "MovementHistoryResponse",
    
    # Services
    "MovementService", "ContactService",
    
    # Integrations
    "create_sale_movement", "create_exhibition_movement"
]
