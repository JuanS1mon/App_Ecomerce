# Imports de bibliotecas estándar
from typing import Optional, List

# Imports de terceros
from pydantic import BaseModel, Field

# Modelo para representar un rol
class Role(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    
    class Config:
        from_attributes = True

class Usuarios(BaseModel):
    codigo: int
    usuario: str
    nombre: str   
    mail: str
    telefono: Optional[str] = None

class UserDB(BaseModel):
    codigo: Optional[int] = Field(None, description="Código del usuario, generado automáticamente")
    usuario: str
    nombre: str
    mail: str  # Este campo debe concordar con el que usas en tus endpoints
    telefono: Optional[str] = None
    direccion: Optional[str] = None  # Falta este campo en tu modelo actual
    fecha_nacimiento: Optional[str] = None  # Falta este campo en tu modelo actual
    activo: bool = True
    clave: Optional[str] = None  # Campo para la contraseña
    roles: List[Role] = []  # Lista de roles que tiene el usuario
    
    class Config:
        from_attributes = True  # Esto permite mapear directamente desde el ORM
        
    def dict(self, *args, **kwargs):
        # Sobrescribir el método dict para no incluir la clave en conversiones a diccionario
        result = super().dict(*args, **kwargs)
        if "clave" in result:
            del result["clave"]
        return result
    
    def has_role(self, role_name: str) -> bool:
        """Verifica si el usuario tiene un rol específico"""
        if not self.roles:
            return False
            
        # Manejar diferentes tipos de objetos de rol
        for role in self.roles:
            # Si el rol es un diccionario
            if isinstance(role, dict) and role.get("nombre") == role_name:
                return True
            # Si el rol es un objeto con atributo nombre
            elif hasattr(role, "nombre") and role.nombre == role_name:
                return True
        return False
    
    def has_any_role(self, role_names: List[str]) -> bool:
        """Verifica si el usuario tiene alguno de los roles especificados"""
        if not self.roles:
            return False
            
        for role in self.roles:
            # Si el rol es un diccionario
            if isinstance(role, dict) and role.get("nombre") in role_names:
                return True
            # Si el rol es un objeto con atributo nombre
            elif hasattr(role, "nombre") and role.nombre in role_names:
                return True
        return False
    
class Usuario(BaseModel):
    codigo: int
    usuario: str
    clave: str
    nombre: str
    mail: str

# Modelo para mostrar usuario con roles (sin incluir la contraseña)
class UsuarioConRoles(BaseModel):
    codigo: int
    usuario: str
    nombre: str
    mail: str
    activo: bool
    roles: List[Role] = []
    
    class Config:
        from_attributes = True

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

# Modelo para asignar roles
class RoleAssignment(BaseModel):
    usuario_id: int
    role_id: int

# Modelo para la creación de roles
class RoleCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

# Esquemas adicionales necesarios para el router
class Token(BaseModel):
    access_token: str
    token_type: str

class Message(BaseModel):
    message: str

class UserCreate(BaseModel):
    usuario: str
    nombre: str
    mail: str
    clave: str
    telefono: Optional[str] = None

class UserLogin(BaseModel):
    usuario: str
    clave: str

class PasswordResetResponse(BaseModel):
    message: str
    success: bool

class ActivationResponse(BaseModel):
    message: str
    success: bool

class ConfirmPasswordReset(BaseModel):
    token: str
    new_password: str
    confirm_password: str

class UserRegistration(BaseModel):
    nombre: str
    usuario: str
    clave: str
    mail: str
    telefono: Optional[str] = None
    acepta_terminos: bool = True

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    usuario: str
    nombre: str
    mail: str
    telefono: Optional[str] = None

class UserPublic(BaseModel):
    codigo: int
    usuario: str
    nombre: str
    mail: str
    activo: bool
    
    class Config:
        from_attributes = True

class UserList(BaseModel):
    usuarios: List[UserPublic]
    total: int

class UserUpdate(BaseModel):
    nombre: Optional[str] = None
    mail: Optional[str] = None
    telefono: Optional[str] = None

class UserUpdateByAdmin(BaseModel):
    nombre: Optional[str] = None
    mail: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None

class UserUpdateByUser(BaseModel):
    nombre: Optional[str] = None
    mail: Optional[str] = None
    telefono: Optional[str] = None

class UserActivate(BaseModel):
    token: str

class AdminUpdate(BaseModel):
    nombre: Optional[str] = None
    mail: Optional[str] = None
    activo: Optional[bool] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class PasswordChange(BaseModel):
    password_actual: str
    password_nueva: str

class EmailRequest(BaseModel):
    email: str

class PhoneRequest(BaseModel):
    telefono: str

class ProfileUpdate(BaseModel):
    nombre: Optional[str] = None
    mail: Optional[str] = None
    telefono: Optional[str] = None

class ResendActivationRequest(BaseModel):
    usuario: str

class SecurePasswordResetRequest(BaseModel):
    email: str