from typing import List
from pydantic import BaseModel
try:
    from ...db.schemas.config.roles import Role
except ImportError:
    from sql_app.db.schemas.config.roles import Role
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