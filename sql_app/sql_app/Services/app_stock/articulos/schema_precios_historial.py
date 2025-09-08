# Imports de bibliotecas estándar
from datetime import datetime
from typing import Optional, List, Dict, Any

# Imports de terceros
from pydantic import BaseModel, ConfigDict, Field

class PreciosHistorialBase(BaseModel):
    articulo_id: int
    precio_anterior: float
    precio_nuevo: float
    tipo_precio: str  # 'costo' o 'venta'
    usuario_id: Optional[int] = None
    motivo: Optional[str] = None
    porcentaje_variacion: Optional[float] = None

class PreciosHistorialCreate(PreciosHistorialBase):
    pass

class PreciosHistorialUpdate(BaseModel):
    usuario_id: Optional[int] = None
    motivo: Optional[str] = None

class PreciosHistorialRead(PreciosHistorialBase):
    id: int
    fecha_cambio: datetime
    model_config = ConfigDict(from_attributes=True)

class PreciosHistorialFiltro(BaseModel):
    """Esquema para realizar búsquedas avanzadas en el historial de precios"""
    articulo_id: Optional[int] = None
    tipo_precio: Optional[str] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    usuario_id: Optional[int] = None