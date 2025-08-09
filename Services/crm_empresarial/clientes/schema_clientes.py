# ============================================================================
# SCHEMAS: CLIENTES
# ============================================================================
"""
Schemas Pydantic para clientes
Parte del servicio: crm_empresarial
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ClientesBase(BaseModel):
    """Schema base para clientes"""
    nombre: str
    email: str
    telefono: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    active: bool


class ClientesCreate(ClientesBase):
    """Schema para crear clientes"""
    pass

class ClientesUpdate(ClientesBase):
    """Schema para actualizar clientes"""
    pass

class ClientesInDB(ClientesBase):
    """Schema para clientes en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    nombre: str
    email: str
    telefono: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    active: bool


# Alias para compatibilidad
Clientes = ClientesInDB
