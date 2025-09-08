# Imports de bibliotecas estándar
from typing import Optional

# Imports de terceros
from pydantic import BaseModel, ConfigDict

class LocationsBase(BaseModel):
    name: str
    city: str
    country: str
    address: Optional[str] = None

class LocationsCreate(LocationsBase):
    id: Optional[int] = None

class LocationsUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    address: Optional[str] = None

class LocationsRead(LocationsBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
