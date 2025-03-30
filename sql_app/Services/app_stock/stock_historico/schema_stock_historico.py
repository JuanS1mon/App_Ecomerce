from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class Stock_historicoBase(BaseModel):
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

class Stock_historicoCreate(Stock_historicoBase):
    id: int

class Stock_historicoUpdate(Stock_historicoBase):
    pass

class Stock_historicoRead(Stock_historicoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
