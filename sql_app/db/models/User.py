from sqlalchemy import Boolean, Column,Integer, String
from ..database import Base
from pydantic import BaseModel

class Usuario_Clase(BaseModel):
    codigo: int
    nombre: str

