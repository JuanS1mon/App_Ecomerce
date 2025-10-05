# ============================================================================
# SCHEMAS: ORDEN_5862
# ============================================================================
"""
Schemas Pydantic para orden_5862
Parte del servicio: sistema_visual_multiple
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Orden_5862Base(BaseModel):
    """Schema base para orden_5862"""
    numero_orden: Optional[str] = None
    fecha_orden: Optional[datetime] = None
    total: Optional[int] = None
    estado: Optional[str] = None
    id_usuario_5862: int


class Orden_5862Create(Orden_5862Base):
    """Schema para crear orden_5862"""
    pass

class Orden_5862Update(Orden_5862Base):
    """Schema para actualizar orden_5862"""
    pass

class Orden_5862InDB(Orden_5862Base):
    """Schema para orden_5862 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    numero_orden: Optional[str] = None
    fecha_orden: Optional[datetime] = None
    total: Optional[int] = None
    estado: Optional[str] = None
    id_usuario_5862: int


# Alias para compatibilidad
Orden_5862 = Orden_5862InDB
