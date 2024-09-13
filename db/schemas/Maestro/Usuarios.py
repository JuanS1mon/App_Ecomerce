from pydantic import BaseModel, Field # Importamos BaseModel de pydantic para crear Usuarios de datos que se utilizarán para validar la entrada de datos y convertir los datos en diferentes formatos.
from typing import Optional


class Usuarios (BaseModel):
    codigo: int
    usuario: str
    nombre: str   
    mail: str
    telefono: Optional[str] = None
class UserDB (Usuarios):
    activo: bool
    clave: str
    codigo: Optional[int] = Field(None, description="Código del usuario, generado automáticamente")


class Usuario(BaseModel):
    codigo: int
    usuario: str
    clave: str
    nombre: str
    mail: str

class PasswordResetRequest(BaseModel):
    email: str


class PasswordReset(BaseModel):
    usuario: str = Field(..., description="Nombre de usuario del que solicita el restablecimiento de contraseña")
    token: str = Field(..., description="Token de restablecimiento de contraseña enviado al correo electrónico")
    new_password: str = Field(..., description="Nueva contraseña que el usuario desea establecer")

class UsuarioCreate(BaseModel):
    usuario: str
    clave: str
    nombre: str
    mail: str

class UsuarioRead(BaseModel):
    codigo: int
    usuario: str
    nombre: str
    mail: str

    class Config:
       from_attributes = True
    
class LoginForm(BaseModel):
    username: str
    password: str