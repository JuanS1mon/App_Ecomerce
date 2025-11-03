from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class CarritosCreate(BaseModel):
    id: Optional[int] = None
    id_usuario: int
    estado: str
    created_at: datetime

class CarritosUpdate(BaseModel):
    id: Optional[int] = None
    id_usuario: Optional[int] = None
    estado: Optional[str] = None
    created_at: Optional[datetime] = None

class CarritosRead(BaseModel):
    id: int
    id_usuario: int
    estado: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
