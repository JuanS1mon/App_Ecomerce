# ============================================================================
# SCHEMAS: USUARIOS
# ============================================================================
"""
Schemas Pydantic para usuarios
Parte del servicio: ecommerce_app
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class UsuariosBase(BaseModel):
    """Schema base para usuarios"""
    nombre: str
    email: str
    password: str
    fecha_registro: datetime


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
    password: str
    fecha_registro: datetime


# Alias para compatibilidad
Usuarios = UsuariosInDB
