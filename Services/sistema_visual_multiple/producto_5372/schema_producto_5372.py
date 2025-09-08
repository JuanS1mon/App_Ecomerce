# ============================================================================
# SCHEMAS: PRODUCTO_5372
# ============================================================================
"""
Schemas Pydantic para producto_5372
Parte del servicio: sistema_visual_multiple
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Producto_5372Base(BaseModel):
    """Schema base para producto_5372"""
    nombre: Optional[str] = None
    precio: Optional[int] = None
    stock: Optional[int] = None
    categoria: Optional[str] = None


class Producto_5372Create(Producto_5372Base):
    """Schema para crear producto_5372"""
    pass

class Producto_5372Update(Producto_5372Base):
    """Schema para actualizar producto_5372"""
    pass

class Producto_5372InDB(Producto_5372Base):
    """Schema para producto_5372 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    nombre: Optional[str] = None
    precio: Optional[int] = None
    stock: Optional[int] = None
    categoria: Optional[str] = None


# Alias para compatibilidad
Producto_5372 = Producto_5372InDB
