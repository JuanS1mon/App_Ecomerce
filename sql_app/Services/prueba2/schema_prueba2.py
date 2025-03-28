from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class Prueba2Base(BaseModel):
    coa: str

class Prueba2Create(Prueba2Base):
    id: int

class Prueba2Update(Prueba2Base):
    pass

class Prueba2Read(Prueba2Base):
    id: int
    model_config = ConfigDict(from_attributes=True)
