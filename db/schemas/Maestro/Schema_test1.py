from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class Test1(BaseModel):

    campo1: int
    campo2: str
    campo3: Optional[float] = 0
    campo4: Optional[bool] = 0

class Test1Read(BaseModel):
    campo1: int
    campo2: str
    campo3: Optional[float] = 0
    campo4: Optional[bool] = 0
