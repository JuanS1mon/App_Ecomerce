# ============================================================================
# SCHEMAS: PRODUCTOS
# ============================================================================
"""
Schemas Pydantic para productos
Parte del servicio: pizzeria_one_man_company
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ProductosBase(BaseModel):
    """Schema base para productos"""
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    precio_venta: int
    porciones: int
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


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
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    precio_venta: int
    porciones: int
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# Alias para compatibilidad
Productos = ProductosInDB
