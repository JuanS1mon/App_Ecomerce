# ============================================================================
# SCHEMAS: T
# ============================================================================
"""
Schemas Pydantic para t
Parte del servicio: test_service
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class TBase(BaseModel):
    """Schema base para t"""


class TCreate(TBase):
    """Schema para crear t"""
    pass

class TUpdate(TBase):
    """Schema para actualizar t"""
    pass

class TInDB(TBase):
    """Schema para t en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None


# Alias para compatibilidad
T = TInDB
