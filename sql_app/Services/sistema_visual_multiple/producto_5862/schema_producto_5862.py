# ============================================================================
# SCHEMAS: PRODUCTO_5862
# ============================================================================
"""
Schemas Pydantic para producto_5862
Parte del servicio: sistema_visual_multiple
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Producto_5862Base(BaseModel):
    """Schema base para producto_5862"""
    nombre: Optional[str] = None
    precio: Optional[int] = None
    stock: Optional[int] = None
    categoria: Optional[str] = None


class Producto_5862Create(Producto_5862Base):
    """Schema para crear producto_5862"""
    pass

class Producto_5862Update(Producto_5862Base):
    """Schema para actualizar producto_5862"""
    pass

class Producto_5862InDB(Producto_5862Base):
    """Schema para producto_5862 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    nombre: Optional[str] = None
    precio: Optional[int] = None
    stock: Optional[int] = None
    categoria: Optional[str] = None


# Alias para compatibilidad
Producto_5862 = Producto_5862InDB
