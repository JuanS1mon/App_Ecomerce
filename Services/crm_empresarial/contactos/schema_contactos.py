# ============================================================================
# SCHEMAS: CONTACTOS
# ============================================================================
"""
Schemas Pydantic para contactos
Parte del servicio: crm_empresarial
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ContactosBase(BaseModel):
    """Schema base para contactos"""
    id_empresa: int
    nombre: str
    email: str
    telefono: Optional[str] = None
    cargo: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    active: bool


class ContactosCreate(ContactosBase):
    """Schema para crear contactos"""
    pass

class ContactosUpdate(ContactosBase):
    """Schema para actualizar contactos"""
    pass

class ContactosInDB(ContactosBase):
    """Schema para contactos en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    id_empresa: int
    nombre: str
    email: str
    telefono: Optional[str] = None
    cargo: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    active: bool


# Alias para compatibilidad
Contactos = ContactosInDB
