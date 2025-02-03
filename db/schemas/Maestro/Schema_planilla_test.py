from typing import Optional
from pydantic import BaseModel, ConfigDict

class Planilla_testBase(BaseModel):
    fecha: str
    origen: str
    tipo: str
    prioridad: str
    caratula: str
    clasificacion: str
    estado: str
    localidad: str
    barrio: str
    lugar: str

class Planilla_testCreate(Planilla_testBase):
    codigo: int

class Planilla_testUpdate(Planilla_testBase):
    pass

class Planilla_testRead(Planilla_testBase):
    codigo: int
    model_config = ConfigDict(from_attributes=True)
