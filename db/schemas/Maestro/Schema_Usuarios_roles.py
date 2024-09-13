from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class Usuarios_roles(BaseModel):

    id: int
    usuario_id: int
    empresa_id: Optional[int] = 0
    rol: Optional[str] = "vacio"
    created_at: Optional[str] = "vacio"
    updated_at: Optional[str] = "vacio"

class Usuarios_rolesRead(BaseModel):
    id: int
    usuario_id: int
    empresa_id: Optional[int] = 0
    rol: Optional[str] = "vacio"
    created_at: Optional[str] = "vacio"
    updated_at: Optional[str] = "vacio"
