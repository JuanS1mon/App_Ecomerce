# ============================================================================
# SCHEMAS: DETALLE_ORDEN_2650
# ============================================================================
"""
Schemas Pydantic para detalle_orden_2650
Parte del servicio: dm3
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Detalle_Orden_2650Base(BaseModel):
    """Schema base para detalle_orden_2650"""
    cantidad: Optional[int] = None
    precio_unitario: Optional[int] = None
    subtotal: Optional[int] = None
    descuento: Optional[int] = None
    orden_2650_id: Optional[int] = None
    producto_2650_id: Optional[int] = None


class Detalle_Orden_2650Create(Detalle_Orden_2650Base):
    """Schema para crear detalle_orden_2650"""
    pass

class Detalle_Orden_2650Update(Detalle_Orden_2650Base):
    """Schema para actualizar detalle_orden_2650"""
    pass

class Detalle_Orden_2650InDB(Detalle_Orden_2650Base):
    """Schema para detalle_orden_2650 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    cantidad: Optional[int] = None
    precio_unitario: Optional[int] = None
    subtotal: Optional[int] = None
    descuento: Optional[int] = None
    orden_2650_id: Optional[int] = None
    producto_2650_id: Optional[int] = None


# Alias para compatibilidad
Detalle_Orden_2650 = Detalle_Orden_2650InDB
