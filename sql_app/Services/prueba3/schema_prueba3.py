from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class Prueba3Base(BaseModel):
    test1: str

class Prueba3Create(Prueba3Base):
    id: int

class Prueba3Update(Prueba3Base):
    pass

class Prueba3Read(Prueba3Base):
    id: int
    model_config = ConfigDict(from_attributes=True)
