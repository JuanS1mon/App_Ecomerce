# ============================================================================
# SCHEMAS: RECETAS
# ============================================================================
"""
Schemas Pydantic para recetas
Parte del servicio: pizzeria_one_man_company
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class RecetasBase(BaseModel):
    """Schema base para recetas"""
    id_producto: int
    id_ingrediente: int
    cantidad: int
    unidad: str
    nota: Optional[str] = None


class RecetasCreate(RecetasBase):
    """Schema para crear recetas"""
    pass

class RecetasUpdate(RecetasBase):
    """Schema para actualizar recetas"""
    pass

class RecetasInDB(RecetasBase):
    """Schema para recetas en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    id_producto: int
    id_ingrediente: int
    cantidad: int
    unidad: str
    nota: Optional[str] = None


# Alias para compatibilidad
Recetas = RecetasInDB
