# ============================================================================
# SCHEMAS: DETALLE_ORDEN_5862
# ============================================================================
"""
Schemas Pydantic para detalle_orden_5862
Parte del servicio: sistema_visual_multiple
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Detalle_Orden_5862Base(BaseModel):
    """Schema base para detalle_orden_5862"""
    cantidad: Optional[int] = None
    precio_unitario: Optional[int] = None
    subtotal: Optional[int] = None
    descuento: Optional[int] = None
    id_orden_5862: int
    id_producto_5862: int


class Detalle_Orden_5862Create(Detalle_Orden_5862Base):
    """Schema para crear detalle_orden_5862"""
    pass

class Detalle_Orden_5862Update(Detalle_Orden_5862Base):
    """Schema para actualizar detalle_orden_5862"""
    pass

class Detalle_Orden_5862InDB(Detalle_Orden_5862Base):
    """Schema para detalle_orden_5862 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    cantidad: Optional[int] = None
    precio_unitario: Optional[int] = None
    subtotal: Optional[int] = None
    descuento: Optional[int] = None
    id_orden_5862: int
    id_producto_5862: int


# Alias para compatibilidad
Detalle_Orden_5862 = Detalle_Orden_5862InDB
