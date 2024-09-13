from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class inventarios(BaseModel):

    id: int
    producto_id: int
    cantidad_fisica: Optional[float] = 0
    inventario_date: Optional[str] = "vacio"
    notas: Optional[str] = "vacio"
    created_at: Optional[str] = "vacio"
    updated_at: Optional[str] = "vacio"

class inventariosRead(BaseModel):
    id: int
    producto_id: int
    cantidad_fisica: Optional[float] = 0
    inventario_date: Optional[str] = "vacio"
    notas: Optional[str] = "vacio"
    created_at: Optional[str] = "vacio"
    updated_at: Optional[str] = "vacio"
