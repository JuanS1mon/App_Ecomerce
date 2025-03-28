from typing import Optional
from pydantic import BaseModel, ConfigDict

class FamiliasBase(BaseModel):
    asd: str

class FamiliasCreate(FamiliasBase):
    tetwe: int

class FamiliasUpdate(FamiliasBase):
    pass

class FamiliasRead(FamiliasBase):
    tetwe: int
    model_config = ConfigDict(from_attributes=True)
