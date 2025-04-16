from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class StockBase(BaseModel):
    nro_movimiento: int
    codigo_art: int
    # Estos campos son opcionales porque no existen en la tabla actual
    id_articulos_serie: Optional[int] = 0
    id_deposito: Optional[int] = 0
    cant_disponible: Optional[float] = 0.0
    cant_reservado: Optional[float] = 0.0
    cant_preparado: Optional[float] = 0.0
    tipo: Optional[bool] = False
    fecha: Optional[str] = ""
    observacion: Optional[str] = ""

class StockCreate(StockBase):
    id: int

class StockUpdate(BaseModel):
    nro_movimiento: Optional[int] = None
    codigo_art: Optional[int] = None
    id_articulos_serie: Optional[int] = None
    id_deposito: Optional[int] = None
    cant_disponible: Optional[float] = None
    cant_reservado: Optional[float] = None
    cant_preparado: Optional[float] = None
    tipo: Optional[bool] = None
    fecha: Optional[str] = None
    observacion: Optional[str] = None

class StockRead(StockBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Esquemas adicionales para reportes y dashboard
class StockFilter(BaseModel):
    codigo_art: Optional[int] = None
    id_deposito: Optional[int] = None
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None

class StockReport(BaseModel):
    id: int
    nro_movimiento: int
    codigo_art: int
    descripcion_art: Optional[str] = None
    cantidad: Optional[float] = 0.0
    fecha: Optional[str] = None
    tipo_movimiento: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class DashboardStats(BaseModel):
    total_items: int
    total_value: float
    low_stock_items: List[StockRead]
    recent_movements: List[StockRead]
    model_config = ConfigDict(from_attributes=True)
