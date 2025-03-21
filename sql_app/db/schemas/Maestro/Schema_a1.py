from typing import Optional
from pydantic import BaseModel, ConfigDict

class A1Base(BaseModel):
    b: str

class A1Create(A1Base):
    a: int

class A1Update(A1Base):
    pass

class A1Read(A1Base):
    a: int
    model_config = ConfigDict(from_attributes=True)
