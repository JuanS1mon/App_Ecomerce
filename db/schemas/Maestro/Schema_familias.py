from typing import Optional
from pydantic import BaseModel, ConfigDict

class FamiliasBase(BaseModel):
    descrip: str

class FamiliasCreate(FamiliasBase):
    codigo: int

class FamiliasUpdate(FamiliasBase):
    pass

class FamiliasRead(FamiliasBase):
    codigo: int
    model_config = ConfigDict(from_attributes=True)
