from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class EmpleadosBase(BaseModel):
    legajo: str
    nombre: str
    sector: str
    telefono: str
    email: str
    activo: bool

class EmpleadosCreate(EmpleadosBase):
    id: int

class EmpleadosUpdate(EmpleadosBase):
    pass

class EmpleadosRead(EmpleadosBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
