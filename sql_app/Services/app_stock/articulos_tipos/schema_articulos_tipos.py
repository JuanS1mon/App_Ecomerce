from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class Articulos_tiposBase(BaseModel):
    descripcion: str

class Articulos_tiposCreate(Articulos_tiposBase):
    id: Optional[int] = None

class Articulos_tiposUpdate(Articulos_tiposBase):
    pass

class Articulos_tiposRead(Articulos_tiposBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
