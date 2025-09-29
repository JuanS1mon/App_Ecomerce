# ============================================================================
# SCHEMAS: USUARIO_7306
# ============================================================================
"""
Schemas Pydantic para usuario_7306
Parte del servicio: sistema_visual_multiple
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Usuario_7306Base(BaseModel):
    """Schema base para usuario_7306"""
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None


class Usuario_7306Create(Usuario_7306Base):
    """Schema para crear usuario_7306"""
    pass

class Usuario_7306Update(Usuario_7306Base):
    """Schema para actualizar usuario_7306"""
    pass

class Usuario_7306InDB(Usuario_7306Base):
    """Schema para usuario_7306 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None


# Alias para compatibilidad
Usuario_7306 = Usuario_7306InDB
