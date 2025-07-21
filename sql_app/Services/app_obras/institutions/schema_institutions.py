# Imports de bibliotecas estándar
from typing import Optional

# Imports de terceros
from pydantic import BaseModel, ConfigDict

class InstitutionsBase(BaseModel):
    name: str
    location_id: int

class InstitutionsCreate(InstitutionsBase):
    id: Optional[int] = None

class InstitutionsUpdate(BaseModel):
    name: Optional[str] = None
    location_id: Optional[int] = None

class InstitutionsRead(InstitutionsBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
