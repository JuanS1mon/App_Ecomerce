# ============================================================================
# SCHEMAS: PRODUCTO_2650
# ============================================================================
"""
Schemas Pydantic para producto_2650
Parte del servicio: dm3
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Producto_2650Base(BaseModel):
    """Schema base para producto_2650"""
    nombre: Optional[str] = None
    precio: Optional[int] = None
    stock: Optional[int] = None
    categoria: Optional[str] = None


class Producto_2650Create(Producto_2650Base):
    """Schema para crear producto_2650"""
    pass

class Producto_2650Update(Producto_2650Base):
    """Schema para actualizar producto_2650"""
    pass

class Producto_2650InDB(Producto_2650Base):
    """Schema para producto_2650 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    nombre: Optional[str] = None
    precio: Optional[int] = None
    stock: Optional[int] = None
    categoria: Optional[str] = None


# Alias para compatibilidad
Producto_2650 = Producto_2650InDB
