from typing import Optional
from pydantic import BaseModel, ConfigDict

class TestBase(BaseModel):
    campo1: str

class TestCreate(TestBase):
    id: int

class TestUpdate(TestBase):
    pass

class TestRead(TestBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
