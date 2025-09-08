# ============================================================================
# SCHEMAS: CATEGORIA_2650
# ============================================================================
"""
Schemas Pydantic para categoria_2650
Parte del servicio: dm3
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Categoria_2650Base(BaseModel):
    """Schema base para categoria_2650"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activa: Optional[bool] = None


class Categoria_2650Create(Categoria_2650Base):
    """Schema para crear categoria_2650"""
    pass

class Categoria_2650Update(Categoria_2650Base):
    """Schema para actualizar categoria_2650"""
    pass

class Categoria_2650InDB(Categoria_2650Base):
    """Schema para categoria_2650 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activa: Optional[bool] = None


# Alias para compatibilidad
Categoria_2650 = Categoria_2650InDB
