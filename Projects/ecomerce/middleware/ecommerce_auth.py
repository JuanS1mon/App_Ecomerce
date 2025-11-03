"""
Middleware de Autenticación para E-commerce
============================================

Middleware específico para el sistema de e-commerce que maneja:
1. Autenticación de usuarios de ecomerce_usuarios
2. Extracción de token desde cookie ecommerce_token
3. Redirección a login de e-commerce si no está autenticado
"""

import logging
from typing import Dict, Any, Optional
from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from db.database import get_db
from security.jwt_auth import verify_token, JWTAuthError

# Configurar logger
logger = logging.getLogger("ecommerce_auth")

# Configuración
LOGIN_PAGE_URL = "/ecommerce/login"

class EcommerceAuthenticationError(Exception):
    """Excepción para errores de autenticación en e-commerce"""
    pass

def extract_ecommerce_token(request: Request) -> Optional[str]:
    """
    Extrae el token de e-commerce de la petición.
    
    Args:
        request: Request de FastAPI
        
    Returns:
        Token JWT si se encuentra, None si no
    """
    logger.debug(f"Extracting ecommerce token from request to: {request.url.path}")
    
    # 1. Intentar desde query params
    token = request.query_params.get("token")
    if token:
        logger.debug("Token encontrado en query params")
        return token
    
    # 2. Intentar desde Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        logger.debug("Token encontrado en Authorization header")
        return token
    
    # 3. Intentar desde cookie ecommerce_token
    token = request.cookies.get("ecommerce_token")
    if token:
        logger.debug("Token encontrado en cookie ecommerce_token")
        return token

    logger.debug("No se encontró token de e-commerce en la petición")
    return None

def get_ecommerce_user_from_token(token: str, db: Session) -> Dict[str, Any]:
    """
    Obtiene el usuario de e-commerce desde un token JWT validado
    
    Args:
        token: Token JWT
        db: Sesión de base de datos
        
    Returns:
        Usuario de e-commerce autenticado
        
    Raises:
        EcommerceAuthenticationError: Si el token es inválido o el usuario no existe
    """
    try:
        logger.debug(f"🔍 Verificando token de e-commerce...")
        
        # Verificar token
        token_data = verify_token(token)
        logger.debug(f"🔑 Token válido para usuario: {token_data.username}")
        
        # Buscar usuario en la tabla ecomerce_usuarios
        user_result = db.execute(
            text("""
                SELECT id, nombre, apellido, email, telefono, direccion, 
                       ciudad, provincia, pais, created_at, active
                FROM ecomerce_usuarios 
                WHERE email = :email AND active = 1
            """),
            {"email": token_data.username}
        ).first()
        
        if not user_result:
            raise EcommerceAuthenticationError(f"Usuario de e-commerce no encontrado: {token_data.username}")
        
        user_data = {
            "id": user_result[0],
            "nombre": user_result[1],
            "apellido": user_result[2],
            "email": user_result[3],
            "telefono": user_result[4],
            "direccion": user_result[5],
            "ciudad": user_result[6],
            "provincia": user_result[7],
            "pais": user_result[8],
            "created_at": user_result[9],
            "active": user_result[10]
        }
        
        logger.info(f"✅ Usuario de e-commerce autenticado exitosamente: {user_data['email']}")
        return user_data
        
    except JWTAuthError as e:
        raise EcommerceAuthenticationError(f"Token inválido: {str(e)}")
    except Exception as e:
        logger.error(f"Error obteniendo usuario de e-commerce desde token: {str(e)}")
        raise EcommerceAuthenticationError(f"Error de autenticación: {str(e)}")

async def require_ecommerce_auth(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Dependency que requiere autenticación de e-commerce para servir plantillas HTML.
    
    Si no hay autenticación válida, redirige automáticamente a la página de login de e-commerce.
    Si hay autenticación válida, devuelve datos del usuario de e-commerce.
    
    Args:
        request: Request de FastAPI
        db: Sesión de base de datos
        
    Returns:
        Diccionario con datos del usuario de e-commerce
        
    Raises:
        HTTPException: Redirige a login si no hay autenticación válida
    """
    logger.info(f"Verificando autenticación de e-commerce para: {request.url.path}")
    
    # Extraer token de la petición
    token = extract_ecommerce_token(request)
    
    if not token:
        logger.warning("No se encontró token de e-commerce en la petición")
        # Redirigir directamente al home sin parámetro next
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": LOGIN_PAGE_URL}
        )
    
    try:
        # Verificar token y obtener usuario
        user_data = get_ecommerce_user_from_token(token, db)
        
        logger.info(f"Autenticación de e-commerce exitosa para usuario: {user_data['email']}")
        
        return {
            "user": user_data,
            "is_authenticated": True
        }
        
    except EcommerceAuthenticationError as e:
        logger.warning(f"Error de autenticación de e-commerce: {str(e)}")
        # Redirigir directamente al home sin parámetro next
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": LOGIN_PAGE_URL}
        )
    except Exception as e:
        logger.error(f"Error inesperado procesando usuario de e-commerce: {str(e)}")
        # Redirigir directamente al home sin parámetro next
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": LOGIN_PAGE_URL}
        )

async def get_current_ecommerce_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Obtiene el usuario actual de e-commerce sin redireccionar.
    Útil para APIs que devuelven 401 en lugar de redirigir.
    
    Args:
        request: Request de FastAPI
        db: Sesión de base de datos
        
    Returns:
        Datos del usuario de e-commerce
        
    Raises:
        HTTPException: 401 si no hay autenticación válida
    """
    token = extract_ecommerce_token(request)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de e-commerce requerido"
        )
    
    try:
        user_data = get_ecommerce_user_from_token(token, db)
        return {
            "user": user_data,
            "is_authenticated": True
        }
    except EcommerceAuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

