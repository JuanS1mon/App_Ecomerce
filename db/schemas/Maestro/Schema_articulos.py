from typing import Optional
from pydantic import BaseModel, ConfigDict

class ArticulosBase(BaseModel):
    codigo: str
    descripcion: str
    precio_costo: float
    modelo: str
    marca: str
    id_tipo: int

class ArticulosCreate(ArticulosBase):
    id: int

class ArticulosUpdate(ArticulosBase):
    pass

class ArticulosRead(ArticulosBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
