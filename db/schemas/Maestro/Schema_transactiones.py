from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class transactiones(BaseModel):

    id: int
    producto_id: int
    cantidad: Optional[float] = 0
    transaction_tipo: Optional[str] = "vacio"
    transaction_date: Optional[str] = "vacio"
    usuario_id: Optional[int] = 0
    created_at: Optional[str] = "vacio"
    updated_at: Optional[str] = "vacio"

class transactionesRead(BaseModel):
    id: int
    producto_id: int
    cantidad: Optional[float] = 0
    transaction_tipo: Optional[str] = "vacio"
    transaction_date: Optional[str] = "vacio"
    usuario_id: Optional[int] = 0
    created_at: Optional[str] = "vacio"
    updated_at: Optional[str] = "vacio"
