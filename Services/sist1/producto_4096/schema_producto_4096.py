# ============================================================================
# SCHEMAS: PRODUCTO_4096
# ============================================================================
"""
Schemas Pydantic para producto_4096
Parte del servicio: sist1
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Producto_4096Base(BaseModel):
    """Schema base para producto_4096"""
    nombre: Optional[str] = None
    precio: Optional[int] = None
    stock: Optional[int] = None
    categoria: Optional[str] = None


class Producto_4096Create(Producto_4096Base):
    """Schema para crear producto_4096"""
    pass

class Producto_4096Update(Producto_4096Base):
    """Schema para actualizar producto_4096"""
    pass

class Producto_4096InDB(Producto_4096Base):
    """Schema para producto_4096 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    nombre: Optional[str] = None
    precio: Optional[int] = None
    stock: Optional[int] = None
    categoria: Optional[str] = None


# Alias para compatibilidad
Producto_4096 = Producto_4096InDB
