from typing import Optional
from pydantic import BaseModel, ConfigDict

class Pruebat1Base(BaseModel):
    campot2: str
    campot3: float
    campot4: Optional[bool]  # Permitir valores nulos

class Pruebat1Create(Pruebat1Base):
    campot1: int

class Pruebat1Update(Pruebat1Base):
    pass

class Pruebat1Read(Pruebat1Base):
    campot1: int
    model_config = ConfigDict(from_attributes=True)