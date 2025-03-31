from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class Stock_currentBase(BaseModel):
    nro_movimiento: int
    codigo_art: int
    id_deposito: int
    cant_diponible: float
    cant_nodisponible: float
    cant_nodisponible: float
    cant_reservada: float
    cant_preparada: float
    tipo: bool
    fecha: str
    observacion: str

class Stock_currentCreate(Stock_currentBase):
    id: int

class Stock_currentUpdate(Stock_currentBase):
    pass

class Stock_currentRead(Stock_currentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
