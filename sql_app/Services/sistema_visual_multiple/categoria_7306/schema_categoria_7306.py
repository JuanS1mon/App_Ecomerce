# ============================================================================
# SCHEMAS: CATEGORIA_7306
# ============================================================================
"""
Schemas Pydantic para categoria_7306
Parte del servicio: sistema_visual_multiple
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Categoria_7306Base(BaseModel):
    """Schema base para categoria_7306"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activa: Optional[bool] = None


class Categoria_7306Create(Categoria_7306Base):
    """Schema para crear categoria_7306"""
    pass

class Categoria_7306Update(Categoria_7306Base):
    """Schema para actualizar categoria_7306"""
    pass

class Categoria_7306InDB(Categoria_7306Base):
    """Schema para categoria_7306 en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activa: Optional[bool] = None


# Alias para compatibilidad
Categoria_7306 = Categoria_7306InDB
