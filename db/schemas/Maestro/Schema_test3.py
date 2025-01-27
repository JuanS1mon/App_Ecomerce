from typing import Optional
from pydantic import BaseModel, ConfigDict

class Test3Base(BaseModel):
    fecha: str
    nombre: str

class Test3Create(Test3Base):
    codigo: int

class Test3Update(Test3Base):
    pass

class Test3Read(Test3Base):
    codigo: int
    model_config = ConfigDict(from_attributes=True)
