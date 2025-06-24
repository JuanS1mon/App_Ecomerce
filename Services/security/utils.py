# Archivo utilitario para funciones comunes

def encriptar_clave(password: str) -> str:
    """Función para encriptar contraseñas."""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sql_app.db.schemas.config.Usuarios import UserDB
from sql_app.db.database import get_db
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sql_app.config import SECRET_KEY, ALGORITHM
import logging

# Inicializar logger
logger = logging.getLogger("security")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=True)

def get_current_user_for_admin(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserDB:
    """Obtiene usuario actual para el panel de admin"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o no autorizado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = db.query(Usuarios).filter(Usuarios.usuario == username).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except JWTError as e:
        logger.error(f"Error al decodificar JWT: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o no autorizado",
            headers={"WWW-Authenticate": "Bearer"},
        )
