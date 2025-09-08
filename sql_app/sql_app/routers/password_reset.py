"""
Router para la gestión de restablecimiento de contraseñas
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from ..db.database import get_db
from ..db.models.config.usuarios import Usuarios as UsuariosModel
from ..db.schemas.config.Usuarios import SecurePasswordResetRequest, ConfirmPasswordReset
from ..Services.security.security import encriptar_clave, crear_access_token, sanitize_for_log, log_security_event
from ..Services.mail.mail import enviar_email_simple
from sql_app.config import BASE_URL, SECRET_KEY, ALGORITHM

# Configure logger
logger = logging.getLogger(__name__)

# Configuration constants
PASSWORD_RESET_EXPIRE_MINUTES = 60  # 1 hour

# Create timedelta objects for token expiration
password_reset_expires = timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES)

# Intentos de restablecimiento por IP
reset_attempts = {}
max_reset_attempts = 5  # Limitar a 5 intentos por hora por IP

# Helper function to get client info for logging
def get_client_info(request: Request = None) -> dict:
    """Extrae información del cliente para logging de seguridad"""
    if not request:
        return {}
    
    client_ip = "unknown"
    user_agent = "unknown"
    
    try:
        # Obtener IP del cliente
        if hasattr(request, 'client') and request.client:
            client_ip = request.client.host
        elif hasattr(request, 'headers'):
            # Intentar obtener IP de headers de proxy
            x_forwarded_for = request.headers.get("X-Forwarded-For")
            if x_forwarded_for:
                client_ip = x_forwarded_for.split(",")[0].strip()
            else:
                x_real_ip = request.headers.get("X-Real-IP")
                if x_real_ip:
                    client_ip = x_real_ip
        
        # Obtener User-Agent
        if hasattr(request, 'headers'):
            user_agent = request.headers.get("User-Agent", "unknown")
    except Exception:
        pass  # Silenciar errores para no afectar funcionalidad principal
    
    return {
        "ip": client_ip,
        "user_agent": user_agent
    }

# Configuración de Jinja2Templates para plantillas HTML
try:
    templates = Jinja2Templates(directory="sql_app/static")
except Exception as e:
    logger.error(f"Error al inicializar templates: {str(e)}")
    templates = None

router = APIRouter(
    tags=["password-reset"],
    responses={404: {"description": "Not Found"}},
)

@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    """Página de recuperación de contraseña"""
    if templates is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sistema de plantillas no disponible"
        )
    return templates.TemplateResponse("reset_password.html", {"request": request})

@router.post("/password-reset-request")
async def password_reset_request(
    request_data: SecurePasswordResetRequest, 
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Solicita reset de contraseña con protecciones de seguridad"""
    client_info = get_client_info(request)
    
    try:
        # Rate limiting por IP
        client_ip = client_info.get("ip", "unknown")
        current_time = datetime.now()
        
        # Limpiar intentos antiguos (más de 1 hora)
        reset_attempts[client_ip] = [
            attempt for attempt in reset_attempts.get(client_ip, [])
            if current_time - attempt < timedelta(hours=1)
        ]
        
        # Verificar límite de intentos
        if len(reset_attempts.get(client_ip, [])) >= max_reset_attempts:
            log_security_event(
                "PASSWORD_RESET_RATE_LIMIT_EXCEEDED",
                {"email": sanitize_for_log(request_data.email), **client_info},
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiados intentos de restablecimiento. Intenta de nuevo en 1 hora."
            )
        
        # Registrar intento
        reset_attempts.setdefault(client_ip, []).append(current_time)
        
        logger.info(f"Password reset request recibida para: {sanitize_for_log(request_data.email)}")
        
        # Buscar usuario por email
        user = db.query(UsuariosModel).filter(
            UsuariosModel.mail == request_data.email
        ).first()
        
        if user:
            logger.info(f"Creando token para usuario: {sanitize_for_log(user.usuario)}")
            
            # Crear token JWT con información del usuario
            token_data = {
                "sub": user.usuario,
                "email": user.mail,
                "type": "password_reset",
                "exp": datetime.utcnow() + password_reset_expires
            }
            
            reset_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
            
            # Crear enlace de restablecimiento
            reset_link = f"{BASE_URL}/confirm-password-reset?token={reset_token}"
            
            message = f"""
Hola {user.nombre},

Recibimos una solicitud para restablecer tu contraseña.

Si solicitaste restablecer tu contraseña, haz clic en el siguiente enlace:
{reset_link}

Este enlace expira en {PASSWORD_RESET_EXPIRE_MINUTES} minutos.

Si no solicitaste esto, puedes ignorar este mensaje con seguridad.

Saludos,
El equipo de soporte
            """
            
            try:
                background_tasks.add_task(
                    enviar_email_simple,
                    request_data.email,
                    "Restablecimiento de contraseña - Acción requerida",
                    message
                )
                logger.info("Email programado para envío exitosamente")
                
                log_security_event(
                    "PASSWORD_RESET_TOKEN_SENT",
                    {"email": sanitize_for_log(request_data.email), "user_id": user.codigo, **client_info},
                    "INFO"
                )
            except Exception as email_error:
                logger.error(f"Error programando envío de email: {str(email_error)}")
                log_security_event(
                    "PASSWORD_RESET_EMAIL_ERROR",
                    {"email": sanitize_for_log(request_data.email), "error": str(email_error), **client_info},
                    "ERROR"
                )
        else:
            # Log security event for non-existent email attempts
            log_security_event(
                "PASSWORD_RESET_NONEXISTENT_EMAIL",
                {"email": sanitize_for_log(request_data.email), **client_info},
                "WARNING"
            )
        
        # Respuesta genérica por seguridad (no revelar si el email existe)
        return {
            "message": "Si el correo está registrado, recibirás instrucciones para restablecer tu contraseña",
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en password reset request: {str(e)}")
        log_security_event(
            "PASSWORD_RESET_UNEXPECTED_ERROR",
            {"email": sanitize_for_log(request_data.email), "error": str(e), **client_info},
            "ERROR"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno procesando solicitud"
        )

@router.get("/confirm-password-reset", response_class=HTMLResponse)
async def confirm_password_reset_page(request: Request):
    """Página para confirmar el reset de contraseña con token"""
    if templates is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sistema de plantillas no disponible"
        )
    return templates.TemplateResponse("confirm_password_reset.html", {"request": request})

@router.post("/confirm-password-reset")
async def confirm_password_reset(
    reset_data: ConfirmPasswordReset,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Confirma el reset de contraseña con token y nueva contraseña"""
    client_info = get_client_info(request)
    
    try:
        # Validar que las contraseñas coincidan antes de procesar el token
        if reset_data.new_password != reset_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las contraseñas no coinciden"
            )
        
        # Validar longitud mínima de contraseña
        if len(reset_data.new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña debe tener al menos 6 caracteres"
            )
        
        # Verificar y decodificar el token
        try:
            payload = jwt.decode(reset_data.token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            token_type = payload.get("type")
            email = payload.get("email")
            
            if not username:
                raise ValueError("Token no contiene username")
                
            if token_type != "password_reset":
                raise ValueError("Token no es de reset de contraseña")
                
        except jwt.ExpiredSignatureError:
            log_security_event(
                "PASSWORD_RESET_TOKEN_EXPIRED",
                {"token": sanitize_for_log(reset_data.token[:20]), **client_info},
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El enlace de restablecimiento ha expirado. Solicita uno nuevo."
            )
        except JWTError as jwt_error:
            log_security_event(
                "PASSWORD_RESET_INVALID_TOKEN",
                {"token": sanitize_for_log(reset_data.token[:20]), "error": str(jwt_error), **client_info},
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enlace de restablecimiento inválido. Solicita uno nuevo."
            )
        except Exception as token_error:
            log_security_event(
                "PASSWORD_RESET_TOKEN_ERROR",
                {"token": sanitize_for_log(reset_data.token[:20]), "error": str(token_error), **client_info},
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enlace de restablecimiento inválido o expirado. Solicita uno nuevo."
            )
        
        # Buscar usuario
        user = db.query(UsuariosModel).filter(UsuariosModel.usuario == username).first()
        
        if not user:
            log_security_event(
                "PASSWORD_RESET_USER_NOT_FOUND",
                {"username": sanitize_for_log(username), **client_info},
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enlace de restablecimiento inválido o expirado"
            )
        
        # Verificar que el email coincida
        if email and user.mail != email:
            log_security_event(
                "PASSWORD_RESET_EMAIL_MISMATCH",
                {"username": sanitize_for_log(username), "expected_email": sanitize_for_log(email), **client_info},
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enlace de restablecimiento inválido o expirado"
            )
        
        # Verificar que la nueva contraseña no sea igual a la actual
        try:
            from ..Services.security.security import verificar_clave
            if verificar_clave(reset_data.new_password, user.clave):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La nueva contraseña debe ser diferente a la actual"
                )
        except Exception:
            # Si hay error verificando, continuar (mejor que fallar)
            pass
        
        # Encriptar nueva contraseña
        new_password_hash = encriptar_clave(reset_data.new_password)
        
        # Actualizar contraseña en base de datos
        user.clave = new_password_hash
        db.commit()
        
        log_security_event(
            "PASSWORD_RESET_COMPLETED",
            {"username": sanitize_for_log(username), "user_id": user.codigo, **client_info},
            "INFO"
        )
        
        # Enviar email de confirmación en background
        confirmation_message = f"""
Hola {user.nombre},

Tu contraseña ha sido cambiada exitosamente el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}.

Detalles del cambio:
- IP: {client_info.get('ip', 'No disponible')}
- Fecha: {datetime.now().strftime('%d de %B de %Y a las %H:%M')}

Si no realizaste esta acción, por favor contacta inmediatamente con nuestro equipo de soporte.

Por tu seguridad, te recomendamos:
- Usar contraseñas únicas y seguras
- No compartir tus credenciales
- Cerrar sesión en dispositivos públicos

Saludos,
El equipo de soporte
        """
        
        try:
            background_tasks.add_task(
                enviar_email_simple,
                user.mail,
                "Contraseña cambiada exitosamente - Notificación de seguridad",
                confirmation_message
            )
        except Exception as email_error:
            # Log pero no fallar si no se puede enviar email de confirmación
            logger.warning(f"No se pudo programar email de confirmación: {str(email_error)}")
        
        return {
            "message": "Contraseña actualizada exitosamente. Puedes iniciar sesión con tu nueva contraseña.",
            "success": True,
            "redirect_url": "/login"  # Para que el frontend pueda redirigir
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en confirm password reset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno procesando solicitud"
        )
