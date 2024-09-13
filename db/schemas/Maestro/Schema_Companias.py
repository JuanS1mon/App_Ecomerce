from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class Companias(BaseModel):

    id: int
    nombre: str
    direccion: Optional[str] = "vacio"
    telefono: Optional[str] = "vacio"
    created_at: Optional[str] = "vacio"
    updated_at: Optional[str] = "vacio"

class CompaniasRead(BaseModel):
    id: int
    nombre: str
    direccion: Optional[str] = "vacio"
    telefono: Optional[str] = "vacio"
    created_at: Optional[str] = "vacio"
    updated_at: Optional[str] = "vacio"
