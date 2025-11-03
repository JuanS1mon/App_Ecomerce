from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class PedidosCreate(BaseModel):
    id: Optional[int] = None
    id_usuario: int
    fecha_pedido: datetime
    total: int
    estado: str

class PedidosUpdate(BaseModel):
    id: Optional[int] = None
    id_usuario: Optional[int] = None
    fecha_pedido: Optional[datetime] = None
    total: Optional[int] = None
    estado: Optional[str] = None

class PedidosRead(BaseModel):
    id: int
    id_usuario: int
    fecha_pedido: datetime
    total: int
    estado: str
    model_config = ConfigDict(from_attributes=True)
