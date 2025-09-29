# ============================================================================
# SCHEMAS: PRODUCTO_7306
# ============================================================================
"""
Schemas Pydantic para producto_7306
Parte del servicio: sistema_visual_multiple
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Producto_7306Base(BaseModel):
    """Schema base para producto_7306"""
    nombre: Optional[str] = None
    precio: Optional[int] = None
    stock: Optional[int] = None
    categoria: Optional[str] = None


class Producto_7306Create(Producto_7306Base):
    """Schema para crear producto_7306"""
    pass

class Producto_7306Update(Producto_7306Base):
    """Schema para actualizar producto_7306"""
    pass

class Producto_7306InDB(Producto_7306Base):
    """Schema para producto_7306 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    nombre: Optional[str] = None
    precio: Optional[int] = None
    stock: Optional[int] = None
    categoria: Optional[str] = None


# Alias para compatibilidad
Producto_7306 = Producto_7306InDB
