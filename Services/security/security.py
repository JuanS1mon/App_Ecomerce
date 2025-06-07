"""
Módulo de seguridad para autenticación y autorización
Basado en security.py con correcciones de imports y sintaxis
"""

from fastapi import HTTPException, Depends, status, Request
from sqlalchemy.orm import Session

# Importaciones de base de datos con soporte híbrido
try:
    # Importaciones relativas (cuando se ejecuta como módulo)
    from ...db.database import get_db
    from ...db.crud.config.Usuarios import get_usuario, user_pass, get_user_from_db
except ImportError:
    # Importaciones absolutas (cuando se ejecuta directamente)
    from ...db.database import get_db
    from ...db.crud.config.Usuarios import get_usuario, user_pass, get_user_from_db

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
import secrets
import hashlib
from pydantic import BaseModel
from typing import Dict, List, Optional, Union

try:
    # Importaciones relativas (cuando se ejecuta como módulo)
    from ...db.schemas.config.Usuarios import UserDB
    from ...db.crud.config.Usuarios import has_role
except ImportError:
    # Importaciones absolutas (cuando se ejecuta directamente)
    from ...db.schemas.config.Usuarios import UserDB
    from ...db.crud.config.Usuarios import has_role

import logging
import re
from urllib.parse import quote

# Configurar el logger
logger = logging.getLogger("security")

# Carga las variables de entorno del archivo .env
load_dotenv()

# Configuración mejorada
SECRET = os.getenv("SECRET")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
REFRESH_TOKEN_DURATION = int(os.getenv("REFRESH_TOKEN_DURATION", 7 * 24 * 60))  # 7 días
ACCESS_TOKEN_DURATION = int(os.getenv("ACCESS_TOKEN_DURATION", 30))  # 30 minutos

# Validaciones de configuración crítica
if not SECRET:
    raise ValueError("SECRET key no configurado en variables de entorno")
if len(SECRET) < 32:
    raise ValueError("SECRET key debe tener al menos 32 caracteres")

# Configuración de logging
logger = logging.getLogger("security")

# Almacén temporal de tokens invalidados (idealmente esto debería estar en una base de datos)
revoked_tokens: Dict[str, datetime] = {}

# Modelo de datos para el token
class TokenData(BaseModel):
    username: Optional[str] = None

# Configuración de passlib y OAuth2
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2 = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)

# Calcular el tiempo de expiración del token
access_token_expires = timedelta(minutes=ACCESS_TOKEN_DURATION)

# ==============================================================================
# FUNCIONES BÁSICAS DE SEGURIDAD
# ==============================================================================

def encriptar_clave(clave):
    """Encripta una contraseña usando bcrypt"""
    return pwd_context.hash(clave)

def verificar_clave(password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash"""
    return pwd_context.verify(password, hashed_password)

def decodifica_token(token: str):
    """Decodifica un token JWT y devuelve el username"""
    if not token:
        logger.warning("Intento de decodificar un token vacío")
        return None
        
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        usuario = payload.get("sub")
        return usuario
    except jwt.ExpiredSignatureError:
        logger.warning("Token expirado")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Token inválido")
        return None

def crear_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token de acceso JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_DURATION)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)

# ==============================================================================
# FUNCIONES DE AUTENTICACIÓN
# ==============================================================================

def authenticate_user(db: Session, username: str, password: str, request: Request = None):
    """
    Autentica un usuario verificando su nombre y contraseña, y devuelve información completa.
    También obtiene los roles del usuario, manejando posibles errores con la tabla de roles.
    """
    try:    
        # Obtener información básica de autenticación
        user_info = user_pass(db, username, password)
        if not user_info:
            logger.warning(f"Intento de inicio de sesión fallido para usuario inexistente: {username}")
            return None
        
        hashed_password = user_info["password"]
        if not verificar_clave(password, hashed_password):
            logger.warning(f"Contraseña incorrecta para usuario: {username}")
            return None
        
        # Obtener información completa del usuario
        try:
            from ...db.models.config.usuarios import usuarios as UsuariosModel
        except ImportError:
            from sql_app.db.models.config.usuarios import usuarios as UsuariosModel
        
        # Obtener el usuario completo de la base de datos
        user = db.query(UsuariosModel).filter(UsuariosModel.usuario == username).first()
        if not user:
            logger.warning(f"Usuario autenticado pero no encontrado en la base de datos: {username}")
            return None
        
        # Crear diccionario con datos completos del usuario
        user_dict = {
            "username": user.usuario,
            "mail": user.mail,
            "nombre": user.nombre,
            "codigo": user.codigo,
            "activo": user.activo,
            "password": hashed_password
        }
        
        # Intentar obtener roles del usuario con SQL directo
        try:
            from sqlalchemy import text
            
            result = db.execute(text("""
                SELECT r.id, r.nombre, r.descripcion
                FROM Roles r
                JOIN UsuariosRol ur ON r.id = ur.rol_id
                WHERE ur.usuario_id = :usuario_id
            """), {"usuario_id": user.codigo})
            
            # Convertir resultados a lista de diccionarios
            roles = [{"id": row[0], "nombre": row[1], "descripcion": row[2]} for row in result]
            
            if roles:
                user_dict["roles"] = roles
                user_dict["rol_principal"] = roles[0]["nombre"]
                logger.info(f"Roles obtenidos para {username}: {[r['nombre'] for r in roles]}")
            else:
                logger.info(f"No se encontraron roles para usuario: {username}")
                user_dict["roles"] = []
                
        except Exception as e:
            logger.warning(f"Error al obtener roles para {username}: {str(e)}")
            user_dict["roles"] = []
        
        logger.info(f"Usuario autenticado exitosamente: {username}")
        return user_dict
        
    except Exception as e:
        logger.error(f"Error en authenticate_user: {str(e)}")
        return None

# ==============================================================================
# FUNCIONES DE AUTORIZACIÓN
# ==============================================================================

async def get_current_user(request: Request = None, token: str = Depends(oauth2), db: Session = Depends(get_db)):
    """
    Obtiene el usuario actual a partir del token JWT
    """
    try:
        if not token:
            logger.warning("Token no proporcionado")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token no proporcionado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar si el token está revocado
        if token in revoked_tokens:
            if datetime.utcnow() > revoked_tokens[token]:
                # Limpiar token expirado
                del revoked_tokens[token]
            else:
                logger.warning("Intento de uso de token revocado")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token revocado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        # Decodificar token
        username = decodifica_token(token)
        if not username:
            logger.warning("Token inválido o expirado")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Obtener usuario de la base de datos
        user = get_user_from_db(db, username)
        if user is None:
            logger.warning(f"Usuario no encontrado en la base de datos: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Convertir el usuario a objeto UserDB si es un diccionario
        if isinstance(user, dict):
            # Verificar si el usuario está activo
            if not user.get("activo", False):
                logger.warning(f"Usuario deshabilitado: {username}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario deshabilitado",
                    headers={"WWW-Authenticate": "Bearer"},                )
            # Extraer los roles si existen
            roles_data = user.get("roles", [])
            roles = []
            
            for role_data in roles_data:
                if isinstance(role_data, dict):
                    try:
                        from sql_app.db.schemas.config.Usuarios import Role
                    except ImportError:
                        from sql_app.db.schemas.config.Usuarios import Role
                    roles.append(Role(**role_data))
                else:
                    roles.append(role_data)
            
            # Convertir el diccionario user a un objeto UserDB
            user_db = UserDB(
                codigo=user.get("codigo"),
                usuario=user.get("usuario"),
                nombre=user.get("nombre"),
                mail=user.get("mail"),
                telefono=user.get("telefono"),
                direccion=user.get("direccion"),
                fecha_nacimiento=user.get("fecha_nacimiento"),
                activo=user.get("activo", True),
                roles=roles
            )
            user = user_db
        else:
            # Ya es un objeto pero verificamos si tiene el atributo activo
            if hasattr(user, "activo") and not user.activo:
                logger.warning(f"Usuario deshabilitado: {username}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario deshabilitado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        logger.info(f"Usuario autenticado correctamente: {username}")
        return user
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión ha expirado. Por favor, inicie sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        logger.warning(f"Error al decodificar token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ==============================================================================
# FUNCIONES DE VALIDACIÓN DE ROLES
# ==============================================================================

def user_has_role(user, role_name: str) -> bool:
    """Verifica si un usuario tiene un rol específico"""
    if not user or not role_name:
        return False
        
    # Sanitizar nombre del rol
    role_name = role_name.strip().lower()
    
    # Si el usuario es un diccionario
    if isinstance(user, dict):
        roles = user.get("roles", [])
        return any(
            role.get("nombre", "").strip().lower() == role_name 
            for role in roles
        )
    
    # Si el usuario es un objeto
    if hasattr(user, "roles") and user.roles:
        if isinstance(user.roles[0], dict):
            return any(
                role.get("nombre", "").strip().lower() == role_name 
                for role in user.roles
            )
        else:
            return any(
                getattr(role, "nombre", "").strip().lower() == role_name 
                for role in user.roles
            )
    
    return False

def user_has_any_role(user, role_names: List[str]) -> bool:
    """Verifica si un usuario tiene alguno de los roles especificados"""
    if not user:
        return False
        
    # Si el usuario es un diccionario
    if isinstance(user, dict):
        if "roles" not in user or not user["roles"]:
            return False
        return any(role.get("nombre") in role_names for role in user["roles"])
    
    # Si el usuario es un objeto
    if hasattr(user, "roles"):
        if not user.roles:
            return False
            
        # Si los roles son diccionarios
        if user.roles and isinstance(user.roles[0], dict):
            return any(role.get("nombre") in role_names for role in user.roles)
        # Si los roles son objetos con propiedad 'nombre'
        elif user.roles and hasattr(user.roles[0], "nombre"):
            return any(role.nombre in role_names for role in user.roles)
        else:
            return any(getattr(role, "nombre", None) in role_names for role in user.roles)
    
    return False

# ==============================================================================
# DEPENDENCIAS DE AUTORIZACIÓN
# ==============================================================================

async def require_role(role_name: str, user = Depends(get_current_user)):
    """Dependencia que requiere que el usuario tenga un rol específico"""
    if not user_has_role(user, role_name):
        # Extraer el nombre de usuario de forma segura
        if isinstance(user, dict):
            username = user.get("usuario", "desconocido")
        else:
            username = getattr(user, "usuario", "desconocido")
            
        logger.warning(f"Acceso denegado: Usuario {username} no tiene el rol {role_name}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Se requiere el rol '{role_name}' para acceder a esta ruta",
            headers={"Location": "/unauthorized"}
        )
    return user

async def require_any_role(role_names: List[str], user = Depends(get_current_user)):
    """Dependencia que requiere que el usuario tenga al menos uno de los roles especificados"""
    if not user_has_any_role(user, role_names):
        # Extraer el nombre de usuario de forma segura
        if isinstance(user, dict):
            username = user.get("usuario", "desconocido")
        else:
            username = getattr(user, "usuario", "desconocido")
            
        logger.warning(f"Acceso denegado: Usuario {username} no tiene ninguno de los roles {role_names}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Se requiere uno de estos roles para acceder: {', '.join(role_names)}",
            headers={"Location": "/unauthorized"}
        )
    return user

async def require_admin(user = Depends(get_current_user)):
    """Dependencia que requiere que el usuario tenga rol de administrador"""
    if not user_has_role(user, "admin"):
        # Extraer el nombre de usuario de forma segura
        if isinstance(user, dict):
            username = user.get("usuario", "desconocido")
        else:
            username = getattr(user, "usuario", "desconocido")
            
        logger.warning(f"Acceso denegado: Usuario {username} no tiene rol de administrador")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador para acceder a esta ruta",
            headers={"Location": "/unauthorized"}
        )
    return user

# ==============================================================================
# FUNCIONES DE UTILIDAD
# ==============================================================================

def revoke_token(token: str, expires_in: Optional[timedelta] = None):
    """Revoca un token JWT agregándolo a la lista de tokens revocados"""
    if not expires_in:
        expires_in = timedelta(minutes=ACCESS_TOKEN_DURATION)
    
    expiration_time = datetime.utcnow() + expires_in
    revoked_tokens[token] = expiration_time
    logger.info(f"Token revocado exitosamente")

def generar_token_activacion(usuario_id):
    """Genera un token de activación para un usuario"""
    payload = {
        "sub": str(usuario_id),
        "type": "activation",
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)

# ==============================================================================
# FUNCIONES DE SEGURIDAD ADICIONALES
# ==============================================================================

def validate_password_strength(password: str) -> bool:
    """
    Valida la fortaleza de una contraseña
    Requiere al menos 8 caracteres, una mayúscula, una minúscula y un número
    """
    if len(password) < 8:
        return False
    
    if not re.search(r"[A-Z]", password):
        return False
    
    if not re.search(r"[a-z]", password):
        return False
    
    if not re.search(r"\d", password):
        return False
    
    return True

def validate_username(username: str) -> bool:
    """
    Valida el formato del nombre de usuario
    Permite solo letras, números y guiones bajos, entre 3 y 50 caracteres
    """
    if not username or len(username) < 3 or len(username) > 50:
        return False
    
    return re.match(r'^[a-zA-Z0-9_]+$', username) is not None

def log_security_event(event_type: str, details: dict, level: str = "INFO"):
    """
    Registra eventos de seguridad
    """
    # Sanitizar datos sensibles antes del logging
    sanitized_details = {}
    for key, value in details.items():
        if key.lower() in ['password', 'token', 'secret']:
            sanitized_details[key] = "***REDACTED***"
        else:
            sanitized_details[key] = str(value)[:100]  # Limitar longitud
    
    log_message = f"SECURITY_EVENT: {event_type} - {sanitized_details}"
    
    if level.upper() == "WARNING":
        logger.warning(log_message)
    elif level.upper() == "ERROR":
        logger.error(log_message)
    else:
        logger.info(log_message)

# ==============================================================================
# ALIASES PARA COMPATIBILIDAD
# ==============================================================================

# Mantener compatibilidad con código existente
current_user = get_current_user
get_authenticated_user = get_current_user
auth_user = get_current_user
