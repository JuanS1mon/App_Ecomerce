"""
Sistema de autenticación JWT puro - Sin cookies
Maneja tokens JWT exclusivamente a través del header Authorization
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from config import SECRET_KEY, ALGORITHM
from db.database import get_db
from db.models.config.usuarios import Usuarios
from db.models.config.roles import Roles, usuario_roles
from db.schemas.config.Usuarios import UserDB, TokenData
from security.security import verificar_clave

# Configurar logger
logger = logging.getLogger("jwt_auth")

# Configurar HTTPBearer para extraer token del header Authorization
security = HTTPBearer(auto_error=False)

# Configuración de token
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hora por defecto

class JWTAuthError(HTTPException):
    """Excepción personalizada para errores de JWT"""
    def __init__(self, detail: str = "No se pudo validar las credenciales"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT de acceso
    
    Args:
        data: Datos a incluir en el token (generalmente {'sub': username})
        expires_delta: Tiempo de expiración personalizado
    
    Returns:
        Token JWT como string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"Token JWT creado exitosamente para: {data.get('sub', 'unknown')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creando token JWT: {str(e)}")
        raise JWTAuthError("Error interno creando token de acceso")

def verify_token(token: str) -> TokenData:
    """
    Verifica y decodifica un token JWT
    
    Args:
        token: Token JWT a verificar
    
    Returns:
        TokenData con información del token
    
    Raises:
        JWTAuthError: Si el token es inválido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            logger.warning("Token JWT sin 'sub' claim")
            raise JWTAuthError("Token inválido")
        
        logger.debug(f"Token verificado exitosamente para usuario: {username}")
        return TokenData(username=username)
    
    except JWTError as e:
        logger.warning(f"Error decodificando token JWT: {str(e)}")
        raise JWTAuthError("Token inválido o expirado")
    except Exception as e:
        logger.error(f"Error inesperado verificando token: {str(e)}")
        raise JWTAuthError("Error verificando token")

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> UserDB:
    """
    Obtiene el usuario actual desde el token JWT en el header Authorization
    
    Args:
        credentials: Credenciales del header Authorization
        db: Sesión de base de datos
    
    Returns:
        Usuario autenticado
    
    Raises:
        JWTAuthError: Si no hay token o es inválido
    """
    if not credentials:
        logger.warning("No se proporcionó token de autorización")
        raise JWTAuthError("Token de acceso requerido")
    
    # Verificar token
    token_data = verify_token(credentials.credentials)
    
    # Buscar usuario en base de datos
    user = db.query(Usuarios).filter(Usuarios.usuario == token_data.username).first()
    
    if not user:
        logger.warning(f"Usuario no encontrado en BD: {token_data.username}")
        raise JWTAuthError("Usuario no encontrado")
    
    if not user.activo:
        logger.warning(f"Usuario inactivo intentó acceder: {token_data.username}")
        raise JWTAuthError("Usuario inactivo")
    
    # Cargar roles del usuario
    roles_query = db.query(Roles.nombre).join(
        usuario_roles, 
        usuario_roles.c.rol_id == Roles.id
    ).filter(
        usuario_roles.c.usuario_id == user.codigo
    ).all()
    
    user.roles = [role[0].lower() for role in roles_query]
    
    logger.debug(f"Usuario autenticado: {user.usuario} con roles: {user.roles}")
    return user

def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[UserDB]:
    """
    Obtiene el usuario actual si está autenticado, sino devuelve None
    Útil para rutas que funcionan con o sin autenticación
    """
    try:
        if not credentials:
            return None
        return get_current_user(credentials, db)
    except:
        return None

def require_role(required_role: str):
    """
    Decorator/dependency para requerir un rol específico
    
    Args:
        required_role: Nombre del rol requerido (ej: "admin", "user")
    
    Returns:
        Función dependency que verifica el rol
    """
    def check_role(current_user: UserDB = Depends(get_current_user)) -> UserDB:
        if not current_user.roles or required_role.lower() not in current_user.roles:
            logger.warning(
                f"Usuario {current_user.usuario} intentó acceder sin rol {required_role}. "
                f"Roles actuales: {current_user.roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rol '{required_role}' requerido"
            )
        
        logger.debug(f"Acceso autorizado para {current_user.usuario} con rol {required_role}")
        return current_user
    
    return check_role

def require_admin(current_user: UserDB = Depends(get_current_user)) -> UserDB:
    """
    Dependency específico para requerir rol de administrador
    """
    if not current_user.roles or "admin" not in current_user.roles:
        logger.warning(
            f"Usuario {current_user.usuario} intentó acceder al panel de admin. "
            f"Roles actuales: {current_user.roles}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso de administrador requerido"
        )
    
    logger.debug(f"Acceso de admin autorizado para {current_user.usuario}")
    return current_user

def authenticate_user_jwt(db: Session, username: str, password: str) -> Optional[dict]:
    """
    Autentica un usuario por username y password
    
    Args:
        db: Sesión de base de datos
        username: Nombre de usuario
        password: Contraseña en texto plano
    
    Returns:
        Diccionario con información del usuario si es válido, None si no
    """
    try:
        # DEBUG: Log detallado de credenciales recibidas
        logger.debug(f"🔐 AUTHENTICATE_USER_JWT DEBUG:")
        logger.debug(f"  Username recibido: '{username}'")
        logger.debug(f"  Password recibido: {'*' * len(password) if password else 'None'} (longitud: {len(password) if password else 0})")
        
        # Buscar usuario
        user = db.query(Usuarios).filter(Usuarios.usuario == username).first()
        
        if not user:
            logger.warning(f"❌ Intento de login con usuario inexistente: {username}")
            return None
            
        logger.debug(f"✅ Usuario encontrado en BD: {user.usuario}")
        logger.debug(f"  Usuario activo: {user.activo}")
        logger.debug(f"  Hash en BD: {user.clave[:20]}... (longitud: {len(user.clave) if user.clave else 0})")

        if not user.activo:
            logger.warning(f"❌ Intento de login con usuario inactivo: {username}")
            return None
        
        # Verificar contraseña
        logger.debug(f"🔑 Verificando contraseña...")
        password_valid = verificar_clave(password, user.clave)
        logger.debug(f"🔑 Resultado verificación: {password_valid}")
        
        if not password_valid:
            logger.warning(f"❌ Contraseña incorrecta para usuario: {username}")
            return None
            
        logger.info(f"✅ Autenticación exitosa para usuario: {username}")

        # Cargar roles
        roles_query = db.query(Roles.nombre).join(
            usuario_roles, 
            usuario_roles.c.rol_id == Roles.id
        ).filter(
            usuario_roles.c.usuario_id == user.codigo
        ).all()
        
        roles = [role[0] for role in roles_query]
        
        user_data = {
            "codigo": user.codigo,
            "username": user.usuario,
            "nombre": user.nombre,
            "email": user.mail,
            "activo": user.activo,
            "roles": roles
        }
        
        logger.info(f"Autenticación exitosa para usuario: {username}")
        return user_data
    
    except Exception as e:
        logger.error(f"Error en autenticación: {str(e)}")
        return None

# Utilidad para logs de seguridad
def log_auth_event(event_type: str, details: dict, level: str = "INFO"):
    """
    Registra eventos de autenticación y seguridad
    
    Args:
        event_type: Tipo de evento (LOGIN_SUCCESS, LOGIN_FAILED, etc.)
        details: Detalles del evento
        level: Nivel de log (INFO, WARNING, ERROR)
    """
    log_message = f"[{event_type}] {details}"
    
    if level.upper() == "ERROR":
        logger.error(log_message)
    elif level.upper() == "WARNING":
        logger.warning(log_message)
    else:
        logger.info(log_message)
