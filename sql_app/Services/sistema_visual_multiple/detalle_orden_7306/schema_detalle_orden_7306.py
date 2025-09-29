# ============================================================================
# SCHEMAS: DETALLE_ORDEN_7306
# ============================================================================
"""
Schemas Pydantic para detalle_orden_7306
Parte del servicio: sistema_visual_multiple
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Detalle_Orden_7306Base(BaseModel):
    """Schema base para detalle_orden_7306"""
    cantidad: Optional[int] = None
    precio_unitario: Optional[int] = None
    subtotal: Optional[int] = None
    descuento: Optional[int] = None
    orden_7306_id: Optional[int] = None
    producto_7306_id: Optional[int] = None


class Detalle_Orden_7306Create(Detalle_Orden_7306Base):
    """Schema para crear detalle_orden_7306"""
    pass

class Detalle_Orden_7306Update(Detalle_Orden_7306Base):
    """Schema para actualizar detalle_orden_7306"""
    pass

class Detalle_Orden_7306InDB(Detalle_Orden_7306Base):
    """Schema para detalle_orden_7306 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    cantidad: Optional[int] = None
    precio_unitario: Optional[int] = None
    subtotal: Optional[int] = None
    descuento: Optional[int] = None
    orden_7306_id: Optional[int] = None
    producto_7306_id: Optional[int] = None


# Alias para compatibilidad
Detalle_Orden_7306 = Detalle_Orden_7306InDB
