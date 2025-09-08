# Imports de bibliotecas estándar
from typing import Optional

# Imports de terceros
from pydantic import BaseModel

class RoleBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    id: int
    
    class Config:
        from_attributes = True

class RoleAssignment(BaseModel):
    usuario_id: int
    role_id: int