# ============================================================================
# SCHEMAS: USUARIO_2650
# ============================================================================
"""
Schemas Pydantic para usuario_2650
Parte del servicio: dm3
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Usuario_2650Base(BaseModel):
    """Schema base para usuario_2650"""
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None


class Usuario_2650Create(Usuario_2650Base):
    """Schema para crear usuario_2650"""
    pass

class Usuario_2650Update(Usuario_2650Base):
    """Schema para actualizar usuario_2650"""
    pass

class Usuario_2650InDB(Usuario_2650Base):
    """Schema para usuario_2650 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None


# Alias para compatibilidad
Usuario_2650 = Usuario_2650InDB
