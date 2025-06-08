# Imports de bibliotecas estándar
from typing import List

# Imports de terceros
from pydantic import BaseModel

# Imports del proyecto
from ...schemas.config.roles import Role# Actualiza tu clase UserDB:

class UserDB(BaseModel):
    codigo: int
    usuario: str
    nombre: str
    mail: str
    activo: bool
    roles: List[Role] = []
    
    class Config:
        orm_mode = True