# ============================================================================
# SCHEMAS: DETALLE_ORDEN_5372
# ============================================================================
"""
Schemas Pydantic para detalle_orden_5372
Parte del servicio: sistema_visual_multiple
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Detalle_Orden_5372Base(BaseModel):
    """Schema base para detalle_orden_5372"""
    cantidad: Optional[int] = None
    precio_unitario: Optional[int] = None
    subtotal: Optional[int] = None
    descuento: Optional[int] = None
    orden_5372_id: Optional[int] = None
    producto_5372_id: Optional[int] = None


class Detalle_Orden_5372Create(Detalle_Orden_5372Base):
    """Schema para crear detalle_orden_5372"""
    pass

class Detalle_Orden_5372Update(Detalle_Orden_5372Base):
    """Schema para actualizar detalle_orden_5372"""
    pass

class Detalle_Orden_5372InDB(Detalle_Orden_5372Base):
    """Schema para detalle_orden_5372 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    cantidad: Optional[int] = None
    precio_unitario: Optional[int] = None
    subtotal: Optional[int] = None
    descuento: Optional[int] = None
    orden_5372_id: Optional[int] = None
    producto_5372_id: Optional[int] = None


# Alias para compatibilidad
Detalle_Orden_5372 = Detalle_Orden_5372InDB
