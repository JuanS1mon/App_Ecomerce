from pydantic import BaseModel, Field # Importamos BaseModel de pydantic para crear Usuarios de datos que se utilizarán para validar la entrada de datos y convertir los datos en diferentes formatos.
from typing import Optional

class Usuario(BaseModel):
    codigo: int
    usuario: str
    clave: str
    nombre: str
    email: str


class UsuarioCreate(BaseModel):
    usuario: str
    clave: str
    nombre: str
    email: str

class UsuarioRead(BaseModel):
    codigo: int
    usuario: str
    nombre: str
    email: str

    class Config:
       from_attributes = True
    
class LoginForm(BaseModel):
    username: str
    password: str