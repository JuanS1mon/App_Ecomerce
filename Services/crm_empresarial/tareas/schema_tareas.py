# ============================================================================
# SCHEMAS: TAREAS
# ============================================================================
"""
Schemas Pydantic para tareas
Parte del servicio: crm_empresarial
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class TareasBase(BaseModel):
    """Schema base para tareas"""
    id_oportunidad: int
    descripcion: str
    fecha_vencimiento: Optional[datetime] = None
    completada: bool
    created_at: datetime
    updated_at: datetime
    active: bool


class TareasCreate(TareasBase):
    """Schema para crear tareas"""
    pass

class TareasUpdate(TareasBase):
    """Schema para actualizar tareas"""
    pass

class TareasInDB(TareasBase):
    """Schema para tareas en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    id_oportunidad: int
    descripcion: str
    fecha_vencimiento: Optional[datetime] = None
    completada: bool
    created_at: datetime
    updated_at: datetime
    active: bool


# Alias para compatibilidad
Tareas = TareasInDB
