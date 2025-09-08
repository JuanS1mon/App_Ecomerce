# ============================================================================
# SCHEMAS: TABLA1
# ============================================================================
"""
Schemas Pydantic para tabla1
Parte del servicio: mi_sistema
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Tabla1Base(BaseModel):
    """Schema base para tabla1"""


class Tabla1Create(Tabla1Base):
    """Schema para crear tabla1"""
    pass

class Tabla1Update(Tabla1Base):
    """Schema para actualizar tabla1"""
    pass

class Tabla1InDB(Tabla1Base):
    """Schema para tabla1 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None


# Alias para compatibilidad
Tabla1 = Tabla1InDB
