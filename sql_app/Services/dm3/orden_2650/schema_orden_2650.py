# ============================================================================
# SCHEMAS: ORDEN_2650
# ============================================================================
"""
Schemas Pydantic para orden_2650
Parte del servicio: dm3
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Orden_2650Base(BaseModel):
    """Schema base para orden_2650"""
    numero_orden: Optional[str] = None
    fecha_orden: Optional[datetime] = None
    total: Optional[int] = None
    estado: Optional[str] = None
    usuario_2650_id: Optional[int] = None


class Orden_2650Create(Orden_2650Base):
    """Schema para crear orden_2650"""
    pass

class Orden_2650Update(Orden_2650Base):
    """Schema para actualizar orden_2650"""
    pass

class Orden_2650InDB(Orden_2650Base):
    """Schema para orden_2650 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    numero_orden: Optional[str] = None
    fecha_orden: Optional[datetime] = None
    total: Optional[int] = None
    estado: Optional[str] = None
    usuario_2650_id: Optional[int] = None


# Alias para compatibilidad
Orden_2650 = Orden_2650InDB
