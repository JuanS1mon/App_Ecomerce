# ============================================================================
# SCHEMAS: ORDEN_5372
# ============================================================================
"""
Schemas Pydantic para orden_5372
Parte del servicio: sistema_visual_multiple
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Orden_5372Base(BaseModel):
    """Schema base para orden_5372"""
    numero_orden: Optional[str] = None
    fecha_orden: Optional[datetime] = None
    total: Optional[int] = None
    estado: Optional[str] = None
    usuario_5372_id: Optional[int] = None


class Orden_5372Create(Orden_5372Base):
    """Schema para crear orden_5372"""
    pass

class Orden_5372Update(Orden_5372Base):
    """Schema para actualizar orden_5372"""
    pass

class Orden_5372InDB(Orden_5372Base):
    """Schema para orden_5372 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    numero_orden: Optional[str] = None
    fecha_orden: Optional[datetime] = None
    total: Optional[int] = None
    estado: Optional[str] = None
    usuario_5372_id: Optional[int] = None


# Alias para compatibilidad
Orden_5372 = Orden_5372InDB
