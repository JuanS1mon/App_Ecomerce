# ============================================================================
# SCHEMAS: USUARIO_8870
# ============================================================================
"""
Schemas Pydantic para usuario_8870
Parte del servicio: sistema_visual_multiple
"""

from pydantic import BaseModel
from typing import Optional

class Usuario8870Base(BaseModel):
    """Schema base para usuario_8870"""
    nombre: str
    email: str
    telefono: Optional[str] = None
    activo: bool

class Usuario8870Create(Usuario8870Base):
    """Schema para crear usuario_8870"""
    pass

class Usuario8870Update(Usuario8870Base):
    """Schema para actualizar usuario_8870"""
    pass

class Usuario8870InDB(Usuario8870Base):
    """Schema para usuario_8870 en base de datos"""
    id: int

    class Config:
        orm_mode = True

# Alias para compatibilidad
Usuario8870 = Usuario8870InDB
