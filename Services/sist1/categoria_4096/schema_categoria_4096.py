# ============================================================================
# SCHEMAS: CATEGORIA_4096
# ============================================================================
"""
Schemas Pydantic para categoria_4096
Parte del servicio: sist1
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Categoria_4096Base(BaseModel):
    """Schema base para categoria_4096"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activa: Optional[bool] = None


class Categoria_4096Create(Categoria_4096Base):
    """Schema para crear categoria_4096"""
    pass

class Categoria_4096Update(Categoria_4096Base):
    """Schema para actualizar categoria_4096"""
    pass

class Categoria_4096InDB(Categoria_4096Base):
    """Schema para categoria_4096 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activa: Optional[bool] = None


# Alias para compatibilidad
Categoria_4096 = Categoria_4096InDB
