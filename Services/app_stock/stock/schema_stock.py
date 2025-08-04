# Imports de bibliotecas estándar
from datetime import date
from typing import Optional, List

# Imports de terceros
from pydantic import BaseModel, ConfigDict

class StockBase(BaseModel):
    nro_movimiento: int
    codigo_art: int
    id_articulos_serie: Optional[int] = 0
    id_deposito: Optional[int] = 0
    cant_disponible: Optional[float] = 0.0
    cant_reservado: Optional[float] = 0.0
    cant_preparado: Optional[float] = 0.0
    tipo: Optional[bool] = False
    fecha: Optional[date] = None
    observacion: Optional[str] = ""
    

class StockCreate(BaseModel):
    nro_movimiento: Optional[int] = None  # ✅ hacerlo opcional
    codigo_art: int
    id_articulos_serie: int
    id_deposito: int
    id_deposito_destino: int  # Solo se usa en la lógica, no existe en BD
    cant_disponible: float
    cant_reservado: float
    cant_preparado: float
    tipo: bool
    fecha: date
    observacion: Optional[str] = None

class StockUpdate(BaseModel):
    nro_movimiento: Optional[int] = None
    codigo_art: Optional[int] = None
    id_articulos_serie: Optional[int] = None
    id_deposito: Optional[int] = None
    cant_disponible: Optional[float] = None
    cant_reservado: Optional[float] = None
    cant_preparado: Optional[float] = None
    tipo: Optional[bool] = None
    fecha: Optional[date] = None
    observacion: Optional[str] = None
    anulado: Optional[bool] = None  # Para anular el movimiento

class StockRead(StockBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

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
