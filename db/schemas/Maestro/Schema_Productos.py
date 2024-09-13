from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class Productos(BaseModel):

    id: int
    nombre: str
    descripcion: Optional[str] = "vacio"
    precio: Optional[float] = 0
    stock_cantidad: Optional[float] = 0
    Id_compania: Optional[int] = 0
    created_at: Optional[str] = "vacio"
    updated_at: Optional[str] = "vacio"

class ProductosRead(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = "vacio"
    precio: Optional[float] = 0
    stock_cantidad: Optional[float] = 0
    Id_compania: Optional[int] = 0
    created_at: Optional[str] = "vacio"
    updated_at: Optional[str] = "vacio"
