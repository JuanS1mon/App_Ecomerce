from typing import Optional
from pydantic import BaseModel, ConfigDict

class RubrosBase(BaseModel):
    test1: str
    test2: float
    test3: bool

class RubrosCreate(RubrosBase):
    codigo: int

class RubrosUpdate(RubrosBase):
    pass

class RubrosRead(RubrosBase):
    codigo: int
    model_config = ConfigDict(from_attributes=True)
