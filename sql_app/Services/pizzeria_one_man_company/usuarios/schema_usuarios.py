# ============================================================================
# SCHEMAS: USUARIOS
# ============================================================================
"""
Schemas Pydantic para usuarios
Parte del servicio: pizzeria_one_man_company
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class UsuariosBase(BaseModel):
    """Schema base para usuarios"""
    nombre: str
    email: str
    rol: str
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class UsuariosCreate(UsuariosBase):
    """Schema para crear usuarios"""
    pass

class UsuariosUpdate(UsuariosBase):
    """Schema para actualizar usuarios"""
    pass

class UsuariosInDB(UsuariosBase):
    """Schema para usuarios en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    nombre: str
    email: str
    rol: str
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# Alias para compatibilidad
Usuarios = UsuariosInDB
