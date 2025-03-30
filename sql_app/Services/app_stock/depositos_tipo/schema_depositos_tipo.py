from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class Depositos_tipoBase(BaseModel):
    descripcion: str

class Depositos_tipoCreate(Depositos_tipoBase):
    id: int

class Depositos_tipoUpdate(Depositos_tipoBase):
    pass

class Depositos_tipoRead(Depositos_tipoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
