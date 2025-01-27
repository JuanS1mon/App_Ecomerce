from typing import Optional
from pydantic import BaseModel, ConfigDict

class Test5Base(BaseModel):
    nombre: str
    fecha: str
    numerito: float
    verif: bool

class Test5Create(Test5Base):
    codigo: int

class Test5Update(Test5Base):
    pass

class Test5Read(Test5Base):
    codigo: int
    model_config = ConfigDict(from_attributes=True)
