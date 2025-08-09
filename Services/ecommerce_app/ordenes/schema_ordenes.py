# ============================================================================
# SCHEMAS: ORDENES
# ============================================================================
"""
Schemas Pydantic para ordenes
Parte del servicio: ecommerce_app
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class OrdenesBase(BaseModel):
    """Schema base para ordenes"""
    usuario_id: int
    fecha_orden: datetime
    total: Decimal


class OrdenesCreate(OrdenesBase):
    """Schema para crear ordenes"""
    pass

class OrdenesUpdate(OrdenesBase):
    """Schema para actualizar ordenes"""
    pass

class OrdenesInDB(OrdenesBase):
    """Schema para ordenes en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    usuario_id: int
    fecha_orden: datetime
    total: Decimal


# Alias para compatibilidad
Ordenes = OrdenesInDB
