# ============================================================================
# SCHEMAS: PRODUCTOS
# ============================================================================
"""
Schemas Pydantic para productos
Parte del servicio: ecommerce_app
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ProductosBase(BaseModel):
    """Schema base para productos"""
    nombre: str
    descripcion: Optional[str] = None
    precio: Decimal
    stock: int


class ProductosCreate(ProductosBase):
    """Schema para crear productos"""
    pass

class ProductosUpdate(ProductosBase):
    """Schema para actualizar productos"""
    pass

class ProductosInDB(ProductosBase):
    """Schema para productos en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    nombre: str
    descripcion: Optional[str] = None
    precio: Decimal
    stock: int


# Alias para compatibilidad
Productos = ProductosInDB
