# Imports de bibliotecas estándar
from typing import Optional

# Imports de terceros
from pydantic import BaseModel, ConfigDict

class ArtworkStatesBase(BaseModel):
    description: str

class ArtworkStatesCreate(ArtworkStatesBase):
    id: Optional[int] = None

class ArtworkStatesUpdate(BaseModel):
    description: Optional[str] = None

class ArtworkStatesRead(ArtworkStatesBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
