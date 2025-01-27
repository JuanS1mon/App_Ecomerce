from typing import Optional
from pydantic import BaseModel, ConfigDict

class TestBase(BaseModel):
    nombre: str

class TestCreate(TestBase):
    codigo: int

class TestUpdate(TestBase):
    pass

class TestRead(TestBase):
    codigo: int
    model_config = ConfigDict(from_attributes=True)
