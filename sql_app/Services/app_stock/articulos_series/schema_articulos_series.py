from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class Articulos_seriesBase(BaseModel):
    serie: str

class Articulos_seriesCreate(Articulos_seriesBase):
    id: int

class Articulos_seriesUpdate(Articulos_seriesBase):
    pass

class Articulos_seriesRead(Articulos_seriesBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
