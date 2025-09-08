# ============================================================================
# SCHEMAS: AUTORES
# ============================================================================
"""
Schemas Pydantic para autores
Parte del servicio: biblioteca_sistema
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class AutoresBase(BaseModel):
    """Schema base para autores"""
    nombre: str
    email: Optional[str] = None
    fecha_creacion: Optional[datetime] = None


class AutoresCreate(AutoresBase):
    """Schema para crear autores"""
    pass

class AutoresUpdate(AutoresBase):
    """Schema para actualizar autores"""
    pass

class AutoresInDB(AutoresBase):
    """Schema para autores en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    nombre: str
    email: Optional[str] = None
    fecha_creacion: Optional[datetime] = None


# Alias para compatibilidad
Autores = AutoresInDB
