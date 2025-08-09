# ============================================================================
# SCHEMAS: EMPRESAS
# ============================================================================
"""
Schemas Pydantic para empresas
Parte del servicio: crm_empresarial
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class EmpresasBase(BaseModel):
    """Schema base para empresas"""
    nombre: str
    sector: Optional[str] = None
    telefono: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    active: bool


class EmpresasCreate(EmpresasBase):
    """Schema para crear empresas"""
    pass

class EmpresasUpdate(EmpresasBase):
    """Schema para actualizar empresas"""
    pass

class EmpresasInDB(EmpresasBase):
    """Schema para empresas en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    nombre: str
    sector: Optional[str] = None
    telefono: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    active: bool


# Alias para compatibilidad
Empresas = EmpresasInDB
