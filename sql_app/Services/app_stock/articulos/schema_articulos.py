from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class ArticulosBase(BaseModel):
    codigo: str
    descripcion: str
    precio_costo: float
    modelo: str
    marca: int
    id_tipo: int

class ArticulosCreate(ArticulosBase):
    id: int

class ArticulosUpdate(ArticulosBase):
    pass

class ArticulosRead(ArticulosBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
