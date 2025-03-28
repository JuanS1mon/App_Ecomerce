from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

class Facu_gayBase(BaseModel):
    codigo: int
    re: str

class Facu_gayCreate(Facu_gayBase):
    id: int

class Facu_gayUpdate(Facu_gayBase):
    pass

class Facu_gayRead(Facu_gayBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
