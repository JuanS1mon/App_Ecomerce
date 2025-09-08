# ============================================================================
# SCHEMAS: USUARIO_5372
# ============================================================================
"""
Schemas Pydantic para usuario_5372
Parte del servicio: sistema_visual_multiple
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Usuario_5372Base(BaseModel):
    """Schema base para usuario_5372"""
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None


class Usuario_5372Create(Usuario_5372Base):
    """Schema para crear usuario_5372"""
    pass

class Usuario_5372Update(Usuario_5372Base):
    """Schema para actualizar usuario_5372"""
    pass

class Usuario_5372InDB(Usuario_5372Base):
    """Schema para usuario_5372 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None


# Alias para compatibilidad
Usuario_5372 = Usuario_5372InDB
