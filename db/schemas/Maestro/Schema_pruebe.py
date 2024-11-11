from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class pruebe(BaseModel):

    campoq: int
    campob: str
    campoc: Optional[float] = 0

class pruebeRead(BaseModel):
    campoq: int
    campob: str
    campoc: Optional[float] = 0
