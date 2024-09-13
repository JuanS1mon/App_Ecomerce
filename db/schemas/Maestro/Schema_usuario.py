from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class usuario(BaseModel):

    id: int
    username: str
    email: Optional[str] = "vacio"
    password_hash: Optional[str] = "vacio"
    created_at: Optional[str] = "vacio"
    updated_at: Optional[str] = "vacio"

class usuarioRead(BaseModel):
    id: int
    username: str
    email: Optional[str] = "vacio"
    password_hash: Optional[str] = "vacio"
    created_at: Optional[str] = "vacio"
    updated_at: Optional[str] = "vacio"
