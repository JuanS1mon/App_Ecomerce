"""
Módulo de autenticación con Google OAuth2
Maneja el flujo de autenticación OAuth2 con Google para usuarios de ecommerce
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI
)
from Projects.ecomerce.models.usuarios import EcomerceUsuarios
from security.ecommerce_auth import hash_password, create_access_token

# Configure logger
logger = logging.getLogger(__name__)

# Configurar OAuth con Authlib
oauth = OAuth()

# Configurar Google OAuth2
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile',
            'prompt': 'select_account',  # Permite al usuario elegir cuenta
        }
    )
    logger.info("✅ Google OAuth2 configurado correctamente")
else:
    logger.warning("⚠️ Google OAuth2 no configurado - faltan GOOGLE_CLIENT_ID o GOOGLE_CLIENT_SECRET")


def get_oauth_client():
    """Obtiene el cliente OAuth configurado"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth2 no está configurado en el servidor"
        )
    return oauth.google


def validate_google_user_info(user_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida y extrae información relevante del usuario de Google
    
    Args:
        user_info: Información del usuario devuelta por Google
        
    Returns:
        Dict con información validada del usuario
        
    Raises:
        HTTPException si la información es inválida
    """
    try:
        # Extraer información requerida
        google_id = user_info.get("sub")
        email = user_info.get("email")
        email_verified = user_info.get("email_verified", False)
        
        if not google_id or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Información de Google incompleta"
            )
        
        if not email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email de Google no está verificado"
            )
        
        # Extraer información opcional
        nombre = user_info.get("given_name", "")
        apellido = user_info.get("family_name", "")
        profile_picture = user_info.get("picture", "")
        
        return {
            "google_id": google_id,
            "email": email,
            "nombre": nombre,
            "apellido": apellido,
            "profile_picture": profile_picture,
            "email_verified": email_verified
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validando información de Google: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error procesando información de Google"
        )


def find_user_by_google_id(db: Session, google_id: str) -> Optional[EcomerceUsuarios]:
    """
    Busca un usuario por su Google ID
    
    Args:
        db: Sesión de base de datos
        google_id: ID único de Google del usuario
        
    Returns:
        Usuario si existe, None si no existe
    """
    try:
        user = db.query(EcomerceUsuarios).filter(
            EcomerceUsuarios.google_id == google_id
        ).first()
        return user
    except Exception as e:
        logger.error(f"Error buscando usuario por Google ID: {str(e)}")
        return None


def find_user_by_email(db: Session, email: str) -> Optional[EcomerceUsuarios]:
    """
    Busca un usuario por su email
    
    Args:
        db: Sesión de base de datos
        email: Email del usuario
        
    Returns:
        Usuario si existe, None si no existe
    """
    try:
        user = db.query(EcomerceUsuarios).filter(
            EcomerceUsuarios.email == email
        ).first()
        return user
    except Exception as e:
        logger.error(f"Error buscando usuario por email: {str(e)}")
        return None


def create_or_update_google_user(
    db: Session, 
    google_user_info: Dict[str, Any]
) -> EcomerceUsuarios:
    """
    Crea un nuevo usuario o actualiza uno existente con información de Google
    
    Args:
        db: Sesión de base de datos
        google_user_info: Información del usuario de Google (ya validada)
        
    Returns:
        Usuario creado o actualizado
        
    Raises:
        HTTPException si hay un error
    """
    try:
        google_id = google_user_info["google_id"]
        email = google_user_info["email"]
        
        # Buscar por Google ID primero
        user = find_user_by_google_id(db, google_id)
        
        if user:
            # Usuario existente con Google - actualizar información
            logger.info(f"Actualizando usuario existente de Google: {email}")
            user.nombre = google_user_info.get("nombre", user.nombre)
            user.apellido = google_user_info.get("apellido", user.apellido)
            user.profile_picture = google_user_info.get("profile_picture", user.profile_picture)
            user.active = True  # Usuarios de Google están verificados
            db.commit()
            db.refresh(user)
            return user
        
        # Buscar por email (usuario local que quiere vincular con Google)
        user = find_user_by_email(db, email)
        
        if user:
            # Usuario local existente - vincular con Google
            if user.auth_provider == 'local':
                logger.info(f"Vinculando usuario local existente con Google: {email}")
                user.google_id = google_id
                user.auth_provider = 'google'
                user.profile_picture = google_user_info.get("profile_picture", user.profile_picture)
                user.active = True
                db.commit()
                db.refresh(user)
                return user
            else:
                # Usuario ya tiene otro proveedor
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Este email ya está registrado con otro método de autenticación"
                )
        
        # Usuario nuevo - crear con Google
        logger.info(f"Creando nuevo usuario desde Google: {email}")
        new_user = EcomerceUsuarios(
            nombre=google_user_info.get("nombre", ""),
            apellido=google_user_info.get("apellido", ""),
            email=email,
            google_id=google_id,
            auth_provider='google',
            profile_picture=google_user_info.get("profile_picture", ""),
            active=True,  # Usuarios de Google están verificados automáticamente
            contraseña_hash=None,  # No necesitan contraseña
            created_at=datetime.now()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"✅ Usuario de Google creado exitosamente: {email}")
        return new_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando/actualizando usuario de Google: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error procesando usuario de Google"
        )


def log_google_auth_event(event_type: str, details: Dict[str, Any], level: str = "INFO"):
    """
    Registra eventos de autenticación con Google en los logs
    
    Args:
        event_type: Tipo de evento (ej: "GOOGLE_LOGIN_SUCCESS")
        details: Detalles del evento
        level: Nivel de log (INFO, WARNING, ERROR)
    """
    log_message = f"Google Auth Event: {event_type} - {details}"
    
    if level == "ERROR":
        logger.error(log_message)
    elif level == "WARNING":
        logger.warning(log_message)
    else:
        logger.info(log_message)
