from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class Depositos_tiposBase(BaseModel):
    descripcion: str

class Depositos_tiposCreate(Depositos_tiposBase):
    # Eliminamos el ID ya que es auto incremental
    pass

class Depositos_tiposUpdate(Depositos_tiposBase):
    pass

class Depositos_tiposRead(Depositos_tiposBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
