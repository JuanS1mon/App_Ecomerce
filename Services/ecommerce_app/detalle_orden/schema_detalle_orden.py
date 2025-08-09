# ============================================================================
# SCHEMAS: DETALLE_ORDEN
# ============================================================================
"""
Schemas Pydantic para detalle_orden
Parte del servicio: ecommerce_app
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Detalle_OrdenBase(BaseModel):
    """Schema base para detalle_orden"""
    orden_id: int
    producto_id: int
    cantidad: int
    precio_unitario: Decimal


class Detalle_OrdenCreate(Detalle_OrdenBase):
    """Schema para crear detalle_orden"""
    pass

class Detalle_OrdenUpdate(Detalle_OrdenBase):
    """Schema para actualizar detalle_orden"""
    pass

class Detalle_OrdenInDB(Detalle_OrdenBase):
    """Schema para detalle_orden en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    orden_id: int
    producto_id: int
    cantidad: int
    precio_unitario: Decimal


# Alias para compatibilidad
Detalle_Orden = Detalle_OrdenInDB
