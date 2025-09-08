# ============================================================================
# SCHEMAS: CATEGORIA_5372
# ============================================================================
"""
Schemas Pydantic para categoria_5372
Parte del servicio: sistema_visual_multiple
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Categoria_5372Base(BaseModel):
    """Schema base para categoria_5372"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activa: Optional[bool] = None


class Categoria_5372Create(Categoria_5372Base):
    """Schema para crear categoria_5372"""
    pass

class Categoria_5372Update(Categoria_5372Base):
    """Schema para actualizar categoria_5372"""
    pass

class Categoria_5372InDB(Categoria_5372Base):
    """Schema para categoria_5372 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activa: Optional[bool] = None


# Alias para compatibilidad
Categoria_5372 = Categoria_5372InDB
