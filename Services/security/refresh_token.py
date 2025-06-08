# Imports de bibliotecas estándar
from datetime import datetime, timedelta, timezone
from db.crud.config.Usuarios import get_user_from_db
from dotenv import load_dotenv
from typing import Dict, Optional
import logging
import os

# Imports de terceros
from fastapi import HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session

# Cargar variables de entorno
load_dotenv()

# Configuración
SECRET = os.getenv("SECRET")
ALGORITHM = os.getenv("ALGORITHM")
REFRESH_TOKEN_DURATION = int(os.getenv("REFRESH_TOKEN_DURATION", 7 * 24 * 60))  # 7 días por defecto
ACCESS_TOKEN_DURATION = int(os.getenv("ACCESS_TOKEN_DURATION", 30))  # 30 minutos por defecto

# Configuración de logging
logger = logging.getLogger("refresh_token")

# Almacén temporal de tokens invalidados (idealmente esto debería estar en una base de datos)
# Clave: token, Valor: tiempo de expiración
revoked_tokens: Dict[str, datetime] = {}

def crear_refresh_token(username: str) -> str:
    """Crea un refresh token para el usuario."""
    payload = {
        "sub": username,
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_DURATION)
    }
    
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    logger.info(f"Refresh token creado para: {username}")
    return token

def verificar_refresh_token(refresh_token: str, db: Session) -> Optional[str]:
    """Verifica un refresh token y devuelve el nombre de usuario si es válido."""
    try:
        # Verificar si el token ha sido revocado
        if refresh_token in revoked_tokens:
            logger.warning(f"Intento de uso de refresh token revocado")
            return None
            
        # Decodificar el token
        payload = jwt.decode(refresh_token, SECRET, algorithms=[ALGORITHM])
        
        # Verificar que es un refresh token
        if payload.get("type") != "refresh":
            logger.warning(f"Token no es un refresh token")
            return None
            
        username = payload.get("sub")
        if not username:
            logger.warning(f"Refresh token no contiene username")
            return None
            
        # Verificar que el usuario existe
        user = get_user_from_db(db, username)
        if not user:
            logger.warning(f"Usuario de refresh token no existe: {username}")
            return None
            
        # Verificar que el usuario está activo
        if not user.activo:
            logger.warning(f"Usuario de refresh token no está activo: {username}")
            return None
            
        logger.info(f"Refresh token válido para: {username}")
        return username
    except JWTError as e:
        logger.warning(f"Error al decodificar refresh token: {str(e)}")
        return None

def revocar_refresh_token(refresh_token: str):
    """Revoca un refresh token."""
    try:
        # Decodificamos sin verificar para obtener la expiración
        payload = jwt.decode(refresh_token, options={"verify_signature": False})
        exp = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
        
        # Almacenar en el diccionario de tokens revocados
        revoked_tokens[refresh_token] = exp
        logger.info(f"Refresh token revocado")
        
        # Limpiar tokens expirados del diccionario
        limpiar_tokens_revocados()
    except Exception as e:
        logger.error(f"Error al revocar refresh token: {str(e)}")

def limpiar_tokens_revocados():
    """Limpia los tokens revocados expirados del diccionario."""
    ahora = datetime.now(timezone.utc)
    tokens_a_eliminar = [token for token, exp in revoked_tokens.items() if exp < ahora]
    
    for token in tokens_a_eliminar:
        del revoked_tokens[token]
    
    if tokens_a_eliminar:
        logger.info(f"Se eliminaron {len(tokens_a_eliminar)} tokens revocados expirados")