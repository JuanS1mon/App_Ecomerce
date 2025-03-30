from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class DepositosBase(BaseModel):
    descripcion: str
    codigo: str
    observacion: str

class DepositosCreate(DepositosBase):
    id: int

class DepositosUpdate(DepositosBase):
    pass

class DepositosRead(DepositosBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
