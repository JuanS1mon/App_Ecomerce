from typing import Optional
from pydantic import BaseModel, ConfigDict

class Test4Base(BaseModel):
    nombre: str
    numero: int
    veri: bool

class Test4Create(Test4Base):
    codigo: int

class Test4Update(Test4Base):
    pass

class Test4Read(Test4Base):
    codigo: int
    model_config = ConfigDict(from_attributes=True)
