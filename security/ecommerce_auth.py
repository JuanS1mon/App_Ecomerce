"""
Sistema de autenticación para usuarios de ecommerce
Maneja login, registro y verificación de usuarios de EcomerceUsuarios
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from passlib.context import CryptContext
from jose import jwt, JWTError
import re

from config import SECRET_KEY, ALGORITHM

# Configurar logger
logger = logging.getLogger(__name__)

# Configuración de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración de tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas para usuarios ecommerce

def hash_password(password: str) -> str:
    """Encripta una contraseña usando bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token JWT de acceso"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_ecommerce_user(db: Session, email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Autentica un usuario de ecommerce

    Args:
        db: Sesión de base de datos
        email: Email del usuario
        password: Contraseña en texto plano

    Returns:
        Diccionario con información del usuario o None si falla la autenticación
    """
    try:
        # Buscar usuario por email
        user_result = db.execute(
            text("""
                SELECT id, nombre, apellido, email, contraseña_hash, telefono,
                       direccion, ciudad, provincia, pais, active, created_at
                FROM ecomerce_usuarios
                WHERE email = :email AND active = 1
            """),
            {"email": email}
        ).first()

        if not user_result:
            logger.warning(f"Usuario ecommerce no encontrado o inactivo: {email}")
            return None

        # Verificar contraseña
        if not verify_password(password, user_result[4]):  # contraseña_hash está en índice 4
            logger.warning(f"Contraseña incorrecta para usuario ecommerce: {email}")
            return None

        # Retornar información del usuario
        user_data = {
            "id": user_result[0],
            "nombre": user_result[1],
            "apellido": user_result[2],
            "email": user_result[3],
            "telefono": user_result[5],
            "direccion": user_result[6],
            "ciudad": user_result[7],
            "provincia": user_result[8],
            "pais": user_result[9],
            "active": user_result[10],
            "created_at": user_result[11].isoformat() if user_result[11] else None,
            "authenticated": True
        }

        logger.info(f"Usuario ecommerce autenticado exitosamente: {email}")
        return user_data

    except Exception as e:
        logger.error(f"Error autenticando usuario ecommerce {email}: {str(e)}")
        return None

def get_current_ecommerce_user(token: str, db: Session) -> Optional[Dict[str, Any]]:
    """
    Obtiene el usuario ecommerce actual desde un token JWT

    Args:
        token: Token JWT
        db: Sesión de base de datos

    Returns:
        Diccionario con información del usuario o None si el token es inválido
    """
    try:
        # Decodificar token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None

        # Verificar que sea un token de ecommerce
        token_type = payload.get("type")
        if token_type != "ecommerce":
            logger.warning(f"Token no es de tipo ecommerce: {token_type}")
            return None

        # Obtener usuario de la base de datos
        user_result = db.execute(
            text("""
                SELECT id, nombre, apellido, email, telefono, direccion,
                       ciudad, provincia, pais, active, created_at
                FROM ecomerce_usuarios
                WHERE email = :email AND active = 1
            """),
            {"email": email}
        ).first()

        if not user_result:
            return None

        return {
            "id": user_result[0],
            "nombre": user_result[1],
            "apellido": user_result[2],
            "email": user_result[3],
            "telefono": user_result[4],
            "direccion": user_result[5],
            "ciudad": user_result[6],
            "provincia": user_result[7],
            "pais": user_result[8],
            "active": user_result[9],
            "created_at": user_result[10].isoformat() if user_result[10] else None,
            "authenticated": True
        }

    except JWTError as e:
        logger.warning(f"Error decodificando token ecommerce: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error obteniendo usuario ecommerce actual: {str(e)}")
        return None

def register_ecommerce_user(db: Session, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Registra un nuevo usuario de ecommerce

    Args:
        db: Sesión de base de datos
        user_data: Datos del usuario a registrar

    Returns:
        Diccionario con información del usuario registrado o None si falla
    """
    try:
        # Validar datos requeridos
        required_fields = ['nombre', 'apellido', 'email', 'contraseña']
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                logger.error(f"Campo requerido faltante: {field}")
                return None

        # Validar formato de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, user_data['email']):
            logger.error(f"Formato de email inválido: {user_data['email']}")
            return None

        # Verificar que el email no esté registrado
        existing_user = db.execute(
            text("SELECT id FROM ecomerce_usuarios WHERE email = :email"),
            {"email": user_data['email']}
        ).first()

        if existing_user:
            logger.warning(f"Email ya registrado: {user_data['email']}")
            return None

        # Validar longitud de contraseña
        if len(user_data['contraseña']) < 6:
            logger.error("Contraseña demasiado corta (mínimo 6 caracteres)")
            return None

        # Hash de la contraseña
        password_hash = hash_password(user_data['contraseña'])

        # Insertar usuario
        insert_query = text("""
            INSERT INTO ecomerce_usuarios
            (nombre, apellido, email, contraseña_hash, telefono, direccion, ciudad, provincia, pais, active)
            VALUES (:nombre, :apellido, :email, :password_hash, :telefono, :direccion,
                    :ciudad, :provincia, :pais, 1)
        """)

        db.execute(insert_query, {
            "nombre": user_data['nombre'],
            "apellido": user_data['apellido'],
            "email": user_data['email'],
            "password_hash": password_hash,
            "telefono": user_data.get('telefono'),
            "direccion": user_data.get('direccion'),
            "ciudad": user_data.get('ciudad'),
            "provincia": user_data.get('provincia'),
            "pais": user_data.get('pais')
        })

        # Obtener el usuario recién insertado
        select_query = text("""
            SELECT id, nombre, apellido, email, telefono, direccion, ciudad, provincia, pais, active, created_at
            FROM ecomerce_usuarios
            WHERE email = :email
        """)
        result = db.execute(select_query, {"email": user_data['email']})
        row = result.first()
        db.commit()

        if not row:
            logger.error("Error al obtener usuario ecommerce recién insertado")
            return None

        # Crear carrito automáticamente para el nuevo usuario
        try:
            cart_query = text("""
                INSERT INTO ecomerce_carritos (id_usuario, estado, created_at)
                VALUES (:user_id, 'activo', GETDATE())
            """)
            db.execute(cart_query, {"user_id": row[0]})
            db.commit()
            logger.info(f"Carrito creado automáticamente para usuario ecommerce: {row[0]}")
        except Exception as cart_error:
            logger.warning(f"No se pudo crear carrito automático para usuario {row[0]}: {str(cart_error)}")
            # No fallar el registro si no se puede crear el carrito
            db.rollback()  # Revertir la transacción del carrito pero mantener el usuario

        user_info = {
            "id": row[0],
            "nombre": row[1],
            "apellido": row[2],
            "email": row[3],
            "telefono": row[4],
            "direccion": row[5],
            "ciudad": row[6],
            "provincia": row[7],
            "pais": row[8],
            "active": row[9],
            "created_at": row[10].isoformat() if row[10] else None,
            "authenticated": False  # Aún no está autenticado
        }

        logger.info(f"Usuario ecommerce registrado exitosamente: {user_data['email']}")
        return user_info

    except Exception as e:
        db.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR EN REGISTRO: {str(e)}")
        print(f"TRACEBACK: {error_details}")
        logger.error(f"Error registrando usuario ecommerce: {str(e)}")
        logger.error(f"Traceback completo: {error_details}")
        return None

def log_ecommerce_auth_event(event_type: str, details: Dict[str, Any], level: str = "INFO"):
    """
    Registra eventos de autenticación de ecommerce

    Args:
        event_type: Tipo de evento (LOGIN_SUCCESS, LOGIN_FAILED, etc.)
        details: Detalles del evento
        level: Nivel de logging
    """
    message = f"ECOMMERCE_AUTH_{event_type}: {details}"

    if level == "ERROR":
        logger.error(message)
    elif level == "WARNING":
        logger.warning(message)
    else:
        logger.info(message)