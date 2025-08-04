# Imports de bibliotecas estándar
from datetime import date
from typing import Optional

# Imports de terceros
from pydantic import BaseModel, ConfigDict

class ExhibitionsBase(BaseModel):
    artwork_id: int
    name: str
    institution_id: int
    curator: str
    start_date: date
    end_date: date
    documentation_url: str

class ExhibitionsCreate(ExhibitionsBase):
    id: Optional[int] = None

class ExhibitionsUpdate(BaseModel):
    artwork_id: Optional[int] = None
    name: Optional[str] = None
    institution_id: Optional[int] = None
    curator: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    documentation_url: Optional[str] = None

class ExhibitionsRead(ExhibitionsBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
