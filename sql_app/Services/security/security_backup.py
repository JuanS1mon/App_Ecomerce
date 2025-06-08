"""
Módulo de seguridad mejorado para autenticación y autorización
Incluye mejoras de seguridad, logging seguro y validación robusta
"""

"""

Módulo de seguridad mejorado para autenticación y autorización
Incluye mejoras de seguridad, logging seguro y validación robusta
"""

"""

Módulo de seguridad mejorado para autenticación y autorización
Incluye mejoras de seguridad, logging seguro y validación robusta
"""

"""

Módulo de seguridad mejorado para autenticación y autorización
Incluye mejoras de seguridad, logging seguro y validación robusta
"""

from fastapi import HTTPException, Depends, status, Request
from sqlalchemy.orm import Session

from db.database import get_db
from db.crud.config.Usuarios import get_usuario, user_pass, get_user_from_dbfrom fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
import secrets
import hashlib
from pydantic import BaseModel
from typing import Dict, List, Optional, Union
from db.schemas.config.Usuarios import UserDB
from db.crud.config.Usuarios import has_role
import logging
from .rate_limit_improved import check_rate_limit, record_successful_login, clear_attempts
import re
from urllib.parse import quote

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

# Configuración de logging seguro
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("security")

# Configuración de rate limiting mejorada
MAX_LOGIN_ATTEMPTS = 5
LOGIN_TIMEOUT_MINUTES = 15
BRUTE_FORCE_THRESHOLD = 10
ADMIN_NOTIFICATION_THRESHOLD = 20

# Almacén seguro de tokens invalidados (mejorar con Redis en producción)
revoked_tokens: Dict[str, datetime] = {}
failed_login_attempts: Dict[str, int] = {}
suspicious_ips: Dict[str, datetime] = {}

# Modelo de datos para el token con validación
class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []
    iat: Optional[int] = None
    jti: Optional[str] = None  # JWT ID para tracking

# Configuración de passlib con múltiples esquemas
pwd_context = CryptContext(
    schemes=["bcrypt", "argon2"],
    deprecated="auto",
    bcrypt__rounds=13,  # Incrementar rondas para mayor seguridad
    argon2__memory_cost=102400,  # 100MB
    argon2__time_cost=2,
    argon2__parallelism=8
)

oauth2 = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)

# Patrones de validación
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]{3,30}$")
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

def validate_username(username: str) -> bool:
    """Valida formato de nombre de usuario"""
    return bool(USERNAME_PATTERN.match(username))

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Valida fortaleza de contraseña"""
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    if len(password) > 128:
        return False, "La contraseña no puede exceder 128 caracteres"
    if not re.search(r"[A-Z]", password):
        return False, "La contraseña debe contener al menos una mayúscula"
    if not re.search(r"[a-z]", password):
        return False, "La contraseña debe contener al menos una minúscula"
    if not re.search(r"\d", password):
        return False, "La contraseña debe contener al menos un número"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "La contraseña debe contener al menos un carácter especial"
    
    # Verificar patrones comunes débiles
    weak_patterns = [
        r"(.)\\1{2,}",  # Caracteres repetidos
        r"(012|123|234|345|456|567|678|789|890)",  # Secuencias numéricas
        r"(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)"  # Secuencias alfabéticas
    ]
    
    for pattern in weak_patterns:
        if re.search(pattern, password.lower()):
            return False, "La contraseña contiene patrones débiles"
    
    return True, "Contraseña válida"

def encriptar_clave(clave: str) -> str:
    """Encripta contraseña con validación previa"""
    if not clave:
        raise ValueError("La contraseña no puede estar vacía")
    
    is_valid, message = validate_password_strength(clave)
    if not is_valid:
        raise ValueError(f"Contraseña inválida: {message}")
    
    return pwd_context.hash(clave)

def verificar_clave(password: str, hashed_password: str) -> bool:
    """Verifica contraseña con protección contra timing attacks"""
    if not password or not hashed_password:
        # Realizar hash dummy para evitar timing attacks
        pwd_context.verify("dummy", "$2b$12$dummy.hash.to.prevent.timing.attacks")
        return False
    
    try:
        return pwd_context.verify(password, hashed_password)
    except Exception as e:
        logger.error(f"Error verificando contraseña: {str(e)}")
        return False

def generate_jti() -> str:
    """Genera un JWT ID único"""
    return secrets.token_urlsafe(32)

def crear_access_token(data: dict, expires_delta: Optional[timedelta] = None, scopes: List[str] = None) -> str:
    """Crea token JWT con seguridad mejorada"""
    to_encode = data.copy()
    
    # Configurar expiración
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_DURATION)
    
    # Añadir claims de seguridad
    jti = generate_jti()
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": jti,
        "scopes": scopes or [],
        "aud": "sql_app",  # Audience
        "iss": "sql_app_auth"  # Issuer
    })
    
    return jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)

def decodifica_token(token: str) -> Optional[dict]:
    """Decodifica token con validaciones de seguridad"""
    if not token:
        logger.warning("Intento de decodificar un token vacío")
        return None
    
    # Validar formato básico del token
    if len(token) > 2048:  # Tokens JWT típicamente < 2KB
        logger.warning("Token demasiado largo, posible ataque")
        return None
        
    try:
        payload = jwt.decode(
            token, 
            SECRET, 
            algorithms=[ALGORITHM],
            audience="sql_app",
            issuer="sql_app_auth",
            options={
                "verify_exp": True,
                "verify_iat": True,
                "verify_aud": True,
                "verify_iss": True
            }
        )
        
        # Verificar si el token está revocado
        jti = payload.get("jti")
        if jti and is_token_revoked(jti):
            logger.warning(f"Token revocado usado: {jti}")
            return None
          return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token expirado")
        return None
    except jwt.InvalidAudienceError:
        logger.warning("Token con audiencia inválida")
        return None
    except jwt.InvalidIssuerError:
        logger.warning("Token con emisor inválido")
        return None
    except JWTError as e:
        logger.warning(f"Token inválido: {str(e)}")
        return None

def is_token_revoked(jti: str) -> bool:
    """Verifica si un token está revocado"""
    if jti in revoked_tokens:
        # Limpiar tokens expirados
        if revoked_tokens[jti] < datetime.now(timezone.utc):
            del revoked_tokens[jti]
            return False
        return True
    return False

def revoke_token(jti: str, expires_at: datetime):
    """Revoca un token específico"""
    revoked_tokens[jti] = expires_at
    logger.info(f"Token revocado: {jti}")

def sanitize_log_data(data: str, max_length: int = 50) -> str:
    """Sanitiza datos para logging seguro"""
    if not data:
        return "[vacío]"
    
    # Eliminar caracteres peligrosos
    sanitized = re.sub(r'[^\w\-@.]', '_', str(data))
    
    # Truncar si es muy largo
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
    
    return sanitized

def log_security_event(event_type: str, details: dict, severity: str = "INFO"):
    """Registra eventos de seguridad de forma segura"""
    sanitized_details = {
        key: sanitize_log_data(str(value)) for key, value in details.items()
    }
    
    log_message = f"SECURITY_{event_type}: {sanitized_details}"
    
    if severity == "WARNING":
        logger.warning(log_message)
    elif severity == "ERROR":
        logger.error(log_message)
    elif severity == "CRITICAL":
        logger.critical(log_message)
    else:
        logger.info(log_message)

def check_suspicious_activity(client_ip: str, username: str = None):
    """Detecta actividad sospechosa"""
    identifier = f"{client_ip}:{username}" if username else client_ip
    
    # Verificar si la IP está marcada como sospechosa
    if client_ip in suspicious_ips:
        time_since_marked = datetime.now(timezone.utc) - suspicious_ips[client_ip]
        if time_since_marked.total_seconds() < 3600:  # 1 hora
            log_security_event(
                "SUSPICIOUS_IP_ACCESS",
                {"ip": client_ip, "username": username or "unknown"},
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado por actividad sospechosa"
            )

def authenticate_user(db: Session, username: str, password: str, request: Request = None) -> Optional[dict]:
    """
    Autentica usuario con seguridad mejorada
    """
    client_ip = request.client.host if request and request.client else "unknown"
    
    # Validaciones de entrada
    if not username or not password:
        log_security_event(
            "INVALID_LOGIN_ATTEMPT",
            {"reason": "empty_credentials", "ip": client_ip},
            "WARNING"
        )
        return None
    
    if not validate_username(username):
        log_security_event(
            "INVALID_LOGIN_ATTEMPT",
            {"reason": "invalid_username_format", "username": username, "ip": client_ip},
            "WARNING"
        )
        return None
    
    # Verificar rate limiting y actividad sospechosa
    if request:
        try:
            check_rate_limit(request, username)
            check_suspicious_activity(client_ip, username)
        except HTTPException:
            raise
    
    try:
        # Obtener información de autenticación
        user_info = user_pass(db, username, password)
        if not user_info:
            log_security_event(
                "LOGIN_FAILED",
                {"reason": "user_not_found", "username": username, "ip": client_ip},
                "WARNING"
            )
            return None
        
        hashed_password = user_info["password"]
        if not verificar_clave(password, hashed_password):
            log_security_event(
                "LOGIN_FAILED",
                {"reason": "invalid_password", "username": username, "ip": client_ip},
                "WARNING"
            )
            return None
          # Obtener información completa del usuario
        try:
            from db.models.config.usuarios import usuarios as UsuariosModel
        except ImportError:
            from db.models.config.usuarios import usuarios as UsuariosModel
        
        user = db.query(UsuariosModel).filter(UsuariosModel.usuario == username).first()
        if not user:
            log_security_event(
                "LOGIN_FAILED",
                {"reason": "user_not_in_db", "username": username, "ip": client_ip},
                "ERROR"
            )
            return None
        
        # Verificar si el usuario está activo
        if not getattr(user, 'activo', True):
            log_security_event(
                "LOGIN_FAILED",
                {"reason": "user_inactive", "username": username, "ip": client_ip},
                "WARNING"
            )
            return None
        
        # Crear diccionario con datos del usuario
        user_dict = {
            "username": user.usuario,
            "mail": user.mail,
            "nombre": user.nombre,
            "codigo": user.codigo,
            "activo": user.activo,
            "password": hashed_password  # Solo para verificaciones internas
        }
        
        # Obtener roles del usuario
        try:
            from sqlalchemy import text
            
            result = db.execute(text("""
                SELECT r.id, r.nombre, r.descripcion
                FROM Roles r
                JOIN UsuariosRol ur ON r.id = ur.rol_id
                WHERE ur.usuario_id = :usuario_id
            """), {"usuario_id": user.codigo})
            
            roles = [{"id": row[0], "nombre": row[1], "descripcion": row[2]} for row in result]
            
            if roles:
                user_dict["roles"] = roles
                user_dict["rol_principal"] = roles[0]["nombre"]
            else:
                user_dict["roles"] = [{"id": 0, "nombre": "usuario", "descripcion": "Usuario estándar"}]
                user_dict["rol_principal"] = "usuario"
        
        except Exception as e:
            logger.error(f"Error obteniendo roles para {username}: {str(e)}")
            user_dict["roles"] = [{"id": 0, "nombre": "usuario", "descripcion": "Usuario estándar"}]
            user_dict["rol_principal"] = "usuario"
        
        # Registrar login exitoso
        if request:
            clear_attempts(request, username)
            record_successful_login(client_ip, username)
        
        log_security_event(
            "LOGIN_SUCCESS",
            {"username": username, "ip": client_ip, "roles": [r["nombre"] for r in user_dict["roles"]]},
            "INFO"
        )
        
        return user_dict
        
    except Exception as e:
        log_security_event(
            "LOGIN_ERROR",
            {"username": username, "ip": client_ip, "error": str(e)},
            "ERROR"
        )
        return None

async def get_current_user_secure(request: Request, db: Session = Depends(get_db)) -> UserDB:
    """
    Obtiene usuario actual con validaciones de seguridad mejoradas
    """
    client_ip = request.client.host if request.client else "unknown"
    
    # Obtener token desde múltiples fuentes
    token = None
    token_source = "none"
    
    # 1. Cookie (preferido para web apps)
    if not token:
        token = request.cookies.get('access_token')
        if token:
            token_source = "cookie"
    
    # 2. Header Authorization
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            token_source = "header"
    
    if not token:
        log_security_event(
            "UNAUTHORIZED_ACCESS",
            {"reason": "no_token", "ip": client_ip, "path": str(request.url.path)},
            "WARNING"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso requerido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Decodificar y validar token
    payload = decodifica_token(token)
    if not payload:
        log_security_event(
            "UNAUTHORIZED_ACCESS",
            {"reason": "invalid_token", "ip": client_ip, "token_source": token_source},
            "WARNING"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = payload.get("sub")
    if not username:
        log_security_event(
            "UNAUTHORIZED_ACCESS",
            {"reason": "no_username_in_token", "ip": client_ip},
            "WARNING"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token malformado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Obtener usuario de la base de datos
    user = get_user_from_db(db, username)
    if not user:
        log_security_event(
            "UNAUTHORIZED_ACCESS",
            {"reason": "user_not_found", "username": username, "ip": client_ip},
            "WARNING"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Convertir a objeto UserDB si es necesario
    if isinstance(user, dict):
        if not user.get("activo", False):
            log_security_event(
                "UNAUTHORIZED_ACCESS",
                {"reason": "user_inactive", "username": username, "ip": client_ip},
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario deshabilitado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        roles_data = user.get("roles", [])
        roles = []
        
        for role_data in roles_data:
            if isinstance(role_data, dict):
                roles.append({
                    "id": role_data.get("id", 0),
                    "nombre": role_data.get("nombre", "usuario"),
                    "descripcion": role_data.get("descripcion", "Usuario estándar")
                })