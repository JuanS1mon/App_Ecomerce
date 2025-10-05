# ============================================================================
# SCHEMAS: INGREDIENTES
# ============================================================================
"""
Schemas Pydantic para ingredientes
Parte del servicio: pizzeria_one_man_company
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class IngredientesBase(BaseModel):
    """Schema base para ingredientes"""
    nombre: str
    unidad_medida: str
    costo_unitario: int
    stock_unidades: int
    punto_reorden: int
    activo: bool
    updated_at: Optional[datetime] = None


class IngredientesCreate(IngredientesBase):
    """Schema para crear ingredientes"""
    pass

class IngredientesUpdate(IngredientesBase):
    """Schema para actualizar ingredientes"""
    pass

class IngredientesInDB(IngredientesBase):
    """Schema para ingredientes en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    nombre: str
    unidad_medida: str
    costo_unitario: int
    stock_unidades: int
    punto_reorden: int
    activo: bool
    updated_at: Optional[datetime] = None


# Alias para compatibilidad
Ingredientes = IngredientesInDB
