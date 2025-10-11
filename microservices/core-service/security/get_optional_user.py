"""
Funciones de autenticación opcional para casos donde el usuario puede o no estar autenticado
"""

"""

Funciones de autenticación opcional para casos donde el usuario puede o no estar autenticado
"""

"""

Funciones de autenticación opcional para casos donde el usuario puede o no estar autenticado
"""

"""

Funciones de autenticación opcional para casos donde el usuario puede o no estar autenticado
"""

from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session


# Importaciones absolutas (cuando se ejecuta directamente)
from ...db.database import get_db
from ...db.schemas.config.Usuarios import UserDB
from ...db.crud.config.Usuarios import get_user_from_db
from jose import jwt, JWTError
import os
import logging

# Configurar logging
logger = logging.getLogger("security")

# Obtener configuración
SECRET = os.getenv("SECRET")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

async def get_optional_user(request: Request, db: Session = Depends(get_db)):
    """
    Obtiene el usuario actual de forma opcional, sin lanzar excepciones si no está autenticado
    
    Args:
        request: Objeto Request de FastAPI
        db: Sesión de base de datos
        
    Returns:
        UserDB | None: Objeto de usuario autenticado o None si no está autenticado
    """
    try:
        # Obtener token de cookies
        token = request.cookies.get('access_token')
        
        if not token:
            # Intentar obtener del header Authorization
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            logger.info("No hay token disponible para autenticación opcional")
            return None
        
        # Decodificar token
        try:
            payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            
            if not username:
                logger.info("Token no contiene username válido")
                return None
            
            # Obtener usuario de la base de datos
            user = get_user_from_db(db, username)
            
            if not user:
                logger.info(f"Usuario no encontrado en la base de datos: {username}")
                return None
            
            # Convertir a UserDB si es necesario            if isinstance(user, dict):
                # Extraer los roles si existen
                roles_data = user.get("roles", [])
                roles = []
                
                # Convertir roles a objetos Role si son diccionarios
                for role_data in roles_data:
                    if isinstance(role_data, dict):
                        from db.schemas.config.Usuarios import Role
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
            
            # Verificar si el usuario está activo
            if hasattr(user, "activo") and not user.activo:
                logger.info(f"Usuario deshabilitado: {username}")
                return None
            
            logger.info(f"Usuario autenticado opcionalmente: {username}")
            return user
            
        except jwt.ExpiredSignatureError:
            logger.info("Token expirado en autenticación opcional")
            return None
        except JWTError as e:
            logger.info(f"Error de JWT en autenticación opcional: {str(e)}")
            return None
            
    except Exception as e:
        logger.error(f"Error en get_optional_user: {str(e)}")
        return None
