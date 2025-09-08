# ============================================================================
# SCHEMAS: ORDEN_4096
# ============================================================================
"""
Schemas Pydantic para orden_4096
Parte del servicio: sist1
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Orden_4096Base(BaseModel):
    """Schema base para orden_4096"""
    numero_orden: Optional[str] = None
    fecha_orden: Optional[datetime] = None
    total: Optional[int] = None
    estado: Optional[str] = None
    usuario_4096_id: Optional[int] = None


class Orden_4096Create(Orden_4096Base):
    """Schema para crear orden_4096"""
    pass

class Orden_4096Update(Orden_4096Base):
    """Schema para actualizar orden_4096"""
    pass

class Orden_4096InDB(Orden_4096Base):
    """Schema para orden_4096 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    numero_orden: Optional[str] = None
    fecha_orden: Optional[datetime] = None
    total: Optional[int] = None
    estado: Optional[str] = None
    usuario_4096_id: Optional[int] = None


# Alias para compatibilidad
Orden_4096 = Orden_4096InDB
