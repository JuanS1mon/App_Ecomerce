from typing import Optional
from pydantic import BaseModel, ConfigDict

class CargaBase(BaseModel):
    fecha: str
    origen: str
    tipo: str
    caratula: str
    clasificacion: str
    estado: str

class CargaCreate(CargaBase):
    nrosuceso: int

class CargaUpdate(CargaBase):
    pass

class CargaRead(CargaBase):
    nrosuceso: int
    model_config = ConfigDict(from_attributes=True)
