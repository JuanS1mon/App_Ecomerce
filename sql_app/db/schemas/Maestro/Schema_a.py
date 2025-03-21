from typing import Optional
from pydantic import BaseModel, ConfigDict

class ABase(BaseModel):
    codigo: str

class ACreate(ABase):
    id: int

class AUpdate(ABase):
    pass

class ARead(ABase):
    id: int
    model_config = ConfigDict(from_attributes=True)
