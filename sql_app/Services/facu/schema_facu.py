from typing import Optional
from pydantic import BaseModel, ConfigDict

class FacuBase(BaseModel):
    asd: str

class FacuCreate(FacuBase):
    id: int

class FacuUpdate(FacuBase):
    pass

class FacuRead(FacuBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
