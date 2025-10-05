# ============================================================================
# SCHEMAS: LIBROS
# ============================================================================
"""
Schemas Pydantic para libros
Parte del servicio: biblioteca_sistema
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class LibrosBase(BaseModel):
    """Schema base para libros"""
    titulo: str
    isbn: str
    autor_id: int
    disponible: bool


class LibrosCreate(LibrosBase):
    """Schema para crear libros"""
    pass

class LibrosUpdate(LibrosBase):
    """Schema para actualizar libros"""
    pass

class LibrosInDB(LibrosBase):
    """Schema para libros en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    titulo: str
    isbn: str
    autor_id: int
    disponible: bool


# Alias para compatibilidad
Libros = LibrosInDB
