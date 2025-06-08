# Imports de bibliotecas estándar
from datetime import date, datetime
from typing import Optional, List, Dict, Any

# Imports de terceros
from pydantic import BaseModel, ConfigDict

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
