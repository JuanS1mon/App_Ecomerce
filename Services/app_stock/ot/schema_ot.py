from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class OtBase(BaseModel):
    id_trabajo: str
    area: str
    personal: str
    tiempo_estimado: str

class OtCreate(OtBase):
    id: int

class OtUpdate(OtBase):
    pass

class OtRead(OtBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
