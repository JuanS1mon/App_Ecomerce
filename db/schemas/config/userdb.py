from typing import List
from pydantic import BaseModel
from db.schemas.config.roles import Role

# Actualiza tu clase UserDB:
class UserDB(BaseModel):
    codigo: int
    usuario: str
    nombre: str
    mail: str
    activo: bool
    roles: List[Role] = []
    
    class Config:
        orm_mode = True