# Imports de bibliotecas estándar
from typing import Optional, List

# Imports de terceros
from pydantic import BaseModel, ConfigDict

class ArtistsBase(BaseModel):
    full_name: str

class ArtistsCreate(ArtistsBase):
    id: Optional[int] = None

class ArtistsUpdate(BaseModel):
    full_name: Optional[str] = None

class ArtistsRead(ArtistsBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
