from typing import Optional
from pydantic import BaseModel, ConfigDict

class Test2Base(BaseModel):
    nombre: str

class Test2Create(Test2Base):
    codigo: int

class Test2Update(Test2Base):
    pass

class Test2Read(Test2Base):
    codigo: int
    model_config = ConfigDict(from_attributes=True)
