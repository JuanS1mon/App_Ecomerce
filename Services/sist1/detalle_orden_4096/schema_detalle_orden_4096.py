# ============================================================================
# SCHEMAS: DETALLE_ORDEN_4096
# ============================================================================
"""
Schemas Pydantic para detalle_orden_4096
Parte del servicio: sist1
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Detalle_Orden_4096Base(BaseModel):
    """Schema base para detalle_orden_4096"""
    cantidad: Optional[int] = None
    precio_unitario: Optional[int] = None
    subtotal: Optional[int] = None
    descuento: Optional[int] = None
    orden_4096_id: Optional[int] = None
    producto_4096_id: Optional[int] = None


class Detalle_Orden_4096Create(Detalle_Orden_4096Base):
    """Schema para crear detalle_orden_4096"""
    pass

class Detalle_Orden_4096Update(Detalle_Orden_4096Base):
    """Schema para actualizar detalle_orden_4096"""
    pass

class Detalle_Orden_4096InDB(Detalle_Orden_4096Base):
    """Schema para detalle_orden_4096 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    cantidad: Optional[int] = None
    precio_unitario: Optional[int] = None
    subtotal: Optional[int] = None
    descuento: Optional[int] = None
    orden_4096_id: Optional[int] = None
    producto_4096_id: Optional[int] = None


# Alias para compatibilidad
Detalle_Orden_4096 = Detalle_Orden_4096InDB
