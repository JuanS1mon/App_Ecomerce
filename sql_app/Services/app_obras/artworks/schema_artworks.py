# Imports de bibliotecas estándar
from typing import Optional

# Imports de terceros
from pydantic import BaseModel, ConfigDict

class ArtworksBase(BaseModel):
    inventory_code: str
    thumbnail_url: Optional[str] = None
    artist_id: int
    title: str
    nickname: Optional[str] = None
    creation_year: int
    technique: str
    materials: str
    dimensions: str
    internal_notes: Optional[str] = None
    photo_credit: Optional[str] = None
    state_id: int
    is_available: bool = True
    is_sold: bool = False
    is_secondary_market: bool = False
    technical_sheet_url: Optional[str] = None

class ArtworksCreate(ArtworksBase):
    id: Optional[int] = None

class ArtworksUpdate(BaseModel):
    inventory_code: Optional[str] = None
    thumbnail_url: Optional[str] = None
    artist_id: Optional[int] = None
    title: Optional[str] = None
    nickname: Optional[str] = None
    creation_year: Optional[int] = None
    technique: Optional[str] = None
    materials: Optional[str] = None
    dimensions: Optional[str] = None
    internal_notes: Optional[str] = None
    photo_credit: Optional[str] = None
    state_id: Optional[int] = None
    is_available: Optional[bool] = None
    is_sold: Optional[bool] = None
    is_secondary_market: Optional[bool] = None
    technical_sheet_url: Optional[str] = None

class ArtworksRead(ArtworksBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
