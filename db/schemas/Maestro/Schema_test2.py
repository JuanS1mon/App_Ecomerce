from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class test2(BaseModel):

    campo1: int
    campo2: str
    campo3: Optional[float] = 0

class test2Read(BaseModel):
    campo1: int
    campo2: str
    campo3: Optional[float] = 0
