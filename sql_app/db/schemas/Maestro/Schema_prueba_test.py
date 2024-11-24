from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class prueba_test(BaseModel):

    campo1: int
    campostr: str
    campofloat: Optional[float] = 0

class prueba_testRead(BaseModel):
    campo1: int
    campostr: str
    campofloat: Optional[float] = 0
