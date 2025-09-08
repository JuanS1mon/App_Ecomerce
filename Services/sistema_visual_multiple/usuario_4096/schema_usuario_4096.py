# ============================================================================
# SCHEMAS: USUARIO_4096
# ============================================================================
"""
Schemas Pydantic para usuario_4096
Parte del servicio: sistema_visual_multiple
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Usuario_4096Base(BaseModel):
    """Schema base para usuario_4096"""
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None


class Usuario_4096Create(Usuario_4096Base):
    """Schema para crear usuario_4096"""
    pass

class Usuario_4096Update(Usuario_4096Base):
    """Schema para actualizar usuario_4096"""
    pass

class Usuario_4096InDB(Usuario_4096Base):
    """Schema para usuario_4096 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None


# Alias para compatibilidad
Usuario_4096 = Usuario_4096InDB
