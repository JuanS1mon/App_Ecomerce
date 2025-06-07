from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class DepositosBase(BaseModel):
    descripcion: str
    codigo: Optional[str] = None
    observacion: Optional[str] = None

class DepositosCreate(DepositosBase):
    # Eliminamos el ID ya que es auto incremental
    pass

class DepositosUpdate(DepositosBase):
    pass

class DepositosRead(DepositosBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
