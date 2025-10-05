# ============================================================================
# SCHEMAS: USUARIO_5862
# ============================================================================
"""
Schemas Pydantic para usuario_5862
Parte del servicio: sistema_visual_multiple
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Usuario_5862Base(BaseModel):
    """Schema base para usuario_5862"""
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None


class Usuario_5862Create(Usuario_5862Base):
    """Schema para crear usuario_5862"""
    pass

class Usuario_5862Update(Usuario_5862Base):
    """Schema para actualizar usuario_5862"""
    pass

class Usuario_5862InDB(Usuario_5862Base):
    """Schema para usuario_5862 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None


# Alias para compatibilidad
Usuario_5862 = Usuario_5862InDB
