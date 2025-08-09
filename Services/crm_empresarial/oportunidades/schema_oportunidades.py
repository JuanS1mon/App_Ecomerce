# ============================================================================
# SCHEMAS: OPORTUNIDADES
# ============================================================================
"""
Schemas Pydantic para oportunidades
Parte del servicio: crm_empresarial
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class OportunidadesBase(BaseModel):
    """Schema base para oportunidades"""
    id_cliente: int
    titulo: str
    monto_estimado: int
    estado: str
    fecha_cierre: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    active: bool


class OportunidadesCreate(OportunidadesBase):
    """Schema para crear oportunidades"""
    pass

class OportunidadesUpdate(OportunidadesBase):
    """Schema para actualizar oportunidades"""
    pass

class OportunidadesInDB(OportunidadesBase):
    """Schema para oportunidades en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    id_cliente: int
    titulo: str
    monto_estimado: int
    estado: str
    fecha_cierre: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    active: bool


# Alias para compatibilidad
Oportunidades = OportunidadesInDB
