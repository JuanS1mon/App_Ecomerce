# ============================================================================
# SCHEMAS: ORDEN_7306
# ============================================================================
"""
Schemas Pydantic para orden_7306
Parte del servicio: sistema_visual_multiple
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Orden_7306Base(BaseModel):
    """Schema base para orden_7306"""
    numero_orden: Optional[str] = None
    fecha_orden: Optional[datetime] = None
    total: Optional[int] = None
    estado: Optional[str] = None
    usuario_7306_id: Optional[int] = None


class Orden_7306Create(Orden_7306Base):
    """Schema para crear orden_7306"""
    pass

class Orden_7306Update(Orden_7306Base):
    """Schema para actualizar orden_7306"""
    pass

class Orden_7306InDB(Orden_7306Base):
    """Schema para orden_7306 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    numero_orden: Optional[str] = None
    fecha_orden: Optional[datetime] = None
    total: Optional[int] = None
    estado: Optional[str] = None
    usuario_7306_id: Optional[int] = None


# Alias para compatibilidad
Orden_7306 = Orden_7306InDB
