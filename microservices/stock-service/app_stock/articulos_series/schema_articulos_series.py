# Imports de bibliotecas estándar
from datetime import date, datetime
from typing import Optional, List, Dict, Any

# Imports de terceros
from pydantic import BaseModel, ConfigDict

class Articulos_seriesBase(BaseModel):
    serie: str

class Articulos_seriesCreate(Articulos_seriesBase):
    id: Optional[int] = None

class Articulos_seriesUpdate(Articulos_seriesBase):
    pass

class Articulos_seriesRead(Articulos_seriesBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
