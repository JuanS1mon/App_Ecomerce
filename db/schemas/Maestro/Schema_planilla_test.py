from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator

class Planilla_testBase(BaseModel):
    fecha: Optional[str] = None
    origen: Optional[str] = None
    tipo: Optional[str] = None
    prioridad: Optional[str] = None
    caratula: Optional[str] = None
    clasificacion: Optional[str] = None
    estado: Optional[str] = None
    localidad: Optional[str] = None
    barrio: Optional[str] = None
    lugar: Optional[str] = None

    @field_validator('fecha', mode='before')
    def parse_fecha(cls, value):
        if isinstance(value, date):
            return value.strftime('%Y-%m-%d')
        return value

class Planilla_testCreate(Planilla_testBase):
    codigo: int

class Planilla_testUpdate(Planilla_testBase):
    pass

class Planilla_testRead(Planilla_testBase):
    codigo: int
    model_config = ConfigDict(from_attributes=True)