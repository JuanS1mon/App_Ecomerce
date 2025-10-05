# ============================================================================
# SCHEMAS: CLIENTES
# ============================================================================
"""
Schemas Pydantic para clientes
Parte del servicio: pizzeria_one_man_company
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ClientesBase(BaseModel):
    """Schema base para clientes"""
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    activo: bool
    created_at: datetime


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
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    activo: bool
    created_at: datetime


# Alias para compatibilidad
Clientes = ClientesInDB
