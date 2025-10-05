# ============================================================================
# SCHEMAS: CATEGORIA_5862
# ============================================================================
"""
Schemas Pydantic para categoria_5862
Parte del servicio: sistema_visual_multiple
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Categoria_5862Base(BaseModel):
    """Schema base para categoria_5862"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activa: Optional[bool] = None


class Categoria_5862Create(Categoria_5862Base):
    """Schema para crear categoria_5862"""
    pass

class Categoria_5862Update(Categoria_5862Base):
    """Schema para actualizar categoria_5862"""
    pass

class Categoria_5862InDB(Categoria_5862Base):
    """Schema para categoria_5862 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activa: Optional[bool] = None


# Alias para compatibilidad
Categoria_5862 = Categoria_5862InDB
