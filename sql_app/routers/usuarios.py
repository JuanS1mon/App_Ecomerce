# ============================================================================
# Router de gestión de usuarios
# ============================================================================
# Este archivo contiene las rutas y lógica para la gestión de usuarios:
# - Registro, activación, edición de perfil, cambio y recuperación de contraseña.
# - Listado y administración de usuarios (solo admin).
# - Compatible con frontend moderno y flujos de autenticación JWT.
#
# Notas de seguridad:
# - La lógica de autenticación y validación de JWT está centralizada en el middleware y servicios de seguridad.
# - No se recomienda definir SECRET_KEY ni ALGORITHM aquí; deben importarse desde la configuración global del proyecto.
#
# Uso recomendado:
# - Mantener este router enfocado en la gestión de usuarios y delegar la autenticación al middleware y dependencias.
# - Usar las constantes y utilidades de config.py o security para claves y algoritmos.
# ============================================================================

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import jwt
from jose import JWTError

# Configure logger
logger = logging.getLogger(__name__)

# =============================
# CONFIGURACIÓN DE CONSTANTES
# =============================
from sql_app.config import FRONTEND_URL as BASE_URL, SECRET, ALGORITHM  # Usar la configuración global

ACTIVATION_TOKEN_EXPIRE_MINUTES = 1440  # 24 horas
PASSWORD_RESET_EXPIRE_MINUTES = 60      # 1 hora

activation_token_expires = timedelta(minutes=ACTIVATION_TOKEN_EXPIRE_MINUTES)
password_reset_expires = timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES)

# Intentos de restablecimiento por IP (rate limiting básico)
reset_attempts = {}
max_reset_attempts = 5  # Limitar a 5 intentos por hora por IP

from fastapi import (APIRouter, BackgroundTasks, Depends, HTTPException, 
                     Request, Response, status)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel

# Project-specific imports
from ..db.database import get_db
from ..db.models.config.usuarios import Usuarios as UsuariosModel
from ..db.schemas.config.Usuarios import (
    UserDB, UserRegistration, UserUpdate, PasswordChange,
    SecurePasswordResetRequest, ConfirmPasswordReset
)

from ..db.crud.config.Usuarios import (
    get_usuario,
    create_usuario,
    update_usuario,
    delete_usuario,
    gets_usuarios
)

from ..Services.security.security import (
    crear_access_token,
    get_current_user_secure,
    get_current_user,
    encriptar_clave,
    sanitize_for_log,
    log_security_event,
    verify_password
)

from ..Services.mail.mail import validar_email, enviar_email_simple
from ..Services.security.get_optional_user import get_optional_user
from ..Services.security.hybrid_validation import validate_password

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
        "client_ip": client_ip,
        "user_agent": user_agent
    }

# Configuración de Jinja2Templates para plantillas HTML
try:
    templates = Jinja2Templates(directory="sql_app/static")
except Exception as e:
    logger.error(f"Error al inicializar templates: {str(e)}")
    templates = None

router = APIRouter(
    prefix="/user",
    tags=["usuarios"],
)

# ============================================================================
# NUEVAS RUTAS PARA COMPATIBILIDAD CON FRONTEND
# ============================================================================

# Router adicional para rutas que el frontend espera con prefijo específico
usuarios_router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios-auth"],
)

@usuarios_router.get("/current")
async def obtener_usuario_actual(
    request: Request,
    response: Response,
    user: UsuariosModel = Depends(get_current_user_secure)
):
    """Obtener información del usuario actualmente autenticado - Compatible con frontend"""
    try:
        # Retornar información del usuario autenticado
        user_data = {
            "id": user.codigo,
            "codigo": user.codigo,
            "usuario": user.usuario,
            "nombre": user.nombre,
            "email": user.mail,
            "mail": user.mail,  # Por compatibilidad
            "autenticado": True,
            "activo": user.activo,
            "fecha_creacion": user.fecha_creacion.isoformat() if hasattr(user, 'fecha_creacion') and user.fecha_creacion else None,
            "ultimo_acceso": user.ultimo_acceso.isoformat() if hasattr(user, 'ultimo_acceso') and user.ultimo_acceso else None
        }
        
        # Incluir roles si están disponibles
        if hasattr(user, "roles") and user.roles:
            user_data["roles"] = [
                {
                    "id": role.id if hasattr(role, 'id') else 0,
                    "nombre": role.nombre if hasattr(role, 'nombre') else str(role),
                    "descripcion": role.descripcion if hasattr(role, 'descripcion') else ""
                }
                for role in user.roles
            ]
        else:
            user_data["roles"] = []
        
        # Determinar si es admin (para compatibilidad frontend)
        is_admin = False
        if hasattr(user, "roles") and user.roles:
            is_admin = any(
                role.nombre.lower() in ['admin', 'administrador'] 
                for role in user.roles
            )
        user_data["is_admin"] = is_admin
        
        return user_data
        
    except Exception as e:
        logger.error(f"Error obteniendo usuario actual: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno obteniendo información del usuario"
        )

# ============================================================================
# RUTAS DE GESTIÓN DE USUARIOS
# ============================================================================

@router.post("/registro")
async def registrar_usuario(
    usuario_data: UserRegistration, 
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Registra nuevo usuario con validaciones de seguridad híbrida (PIN o contraseña segura) y deja inactivo hasta activación por email."""
    client_info = get_client_info(request)
    logger.info(f"Intento de registro: usuario={sanitize_for_log(usuario_data.usuario)}, email={sanitize_for_log(usuario_data.mail)}")
    try:
        # Validar email
        if not validar_email(usuario_data.mail):
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "invalid_email",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    "email": sanitize_for_log(usuario_data.mail),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El email no es válido"
            )
        # Verificar si el usuario ya existe
        existing_user = get_usuario(db, usuario=usuario_data.usuario)
        if existing_user:
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "user_exists",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El nombre de usuario ya está en uso"
            )
        # VALIDACIÓN HÍBRIDA: PIN o contraseña segura
        validation_result = validate_password(usuario_data.clave)
        if not validation_result["valid"]:
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "invalid_password",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    "password_type": validation_result.get("type", "unknown"),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=validation_result["message"]
            )
        # Log tipo de autenticación seleccionado
        auth_type = "PIN" if validation_result.get("type") == "pin" else "Contraseña Segura"
        logger.info(f"Usuario {sanitize_for_log(usuario_data.usuario)} registrado con {auth_type}")
        # Encriptar contraseña
        clave_encriptada = encriptar_clave(usuario_data.clave)
        # Crear usuario INACTIVO
        result = create_usuario(
            db=db,
            nombre=usuario_data.nombre,
            usuario=usuario_data.usuario,
            clave=clave_encriptada,
            mail=usuario_data.mail,
            activo=False  # <-- usuario inactivo hasta activación
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creando usuario"
            )
        # Crear token de activación
        token_activacion = crear_access_token(
            data={"sub": usuario_data.usuario, "type": "activation"},
            expires_delta=activation_token_expires
        )
        # Enviar email de activación
        try:
            if validar_email(usuario_data.mail):
                activation_link = f"{BASE_URL}/user/activar-cuenta?token={token_activacion}"
                background_tasks.add_task(
                    enviar_email_simple,
                    usuario_data.mail,
                    "Activa tu cuenta",
                    f"""
                    Bienvenido/a {usuario_data.nombre},\n\nPor favor activa tu cuenta haciendo clic en el siguiente enlace:\n{activation_link}\n\nEste enlace expira en 24 horas.\n\nSi no solicitaste esto, ignora este mensaje.
                    """
                )
                logger.info(f"Email de activación enviado a {sanitize_for_log(usuario_data.mail)}")
        except Exception as e:
            logger.warning(f"Error validando/enviando email de activación: {str(e)}")
        log_security_event(
            "USER_REGISTERED",
            {
                "usuario": sanitize_for_log(usuario_data.usuario),
                "email": sanitize_for_log(usuario_data.mail),
                **client_info
            },
            "INFO"
        )
        return JSONResponse(
            content={
                "message": "Usuario registrado exitosamente. Revisa tu email para activar la cuenta.",
                "usuario": usuario_data.usuario,
                "activacion_requerida": True
            },
            status_code=status.HTTP_201_CREATED
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en registro: {str(e)}")
        log_security_event(
            "REGISTRATION_ERROR",
            {"error": str(e), **client_info},
            "ERROR"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

# Endpoint de activación de cuenta
from fastapi import Query

@router.get("/activar-cuenta")
async def activar_cuenta(token: str = Query(...), db: Session = Depends(get_db)):
    """Activa la cuenta de usuario usando el token enviado por email."""
    try:
        payload = jwt.decode(token, SECRET.key, algorithms=[ALGORITHM])
        username = payload.get("sub")
        token_type = payload.get("type")
        if not username or token_type != "activation":
            raise HTTPException(status_code=400, detail="Token inválido")
        user = db.query(UsuariosModel).filter(UsuariosModel.usuario == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        if user.activo:
            return {"message": "La cuenta ya está activada"}
        user.activo = True
        db.commit()
        log_security_event(
            "USER_ACTIVATED",
            {"usuario": sanitize_for_log(username)},
            "INFO"
        )
        return {"message": "Cuenta activada exitosamente. Ya puedes iniciar sesión."}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="El enlace de activación ha expirado")
    except Exception as e:
        log_security_event(
            "USER_ACTIVATION_ERROR",
            {"error": str(e)},
            "ERROR"
        )
        raise HTTPException(status_code=400, detail="Token inválido o error de activación")

# ============================================================================
# RUTAS DE GESTIÓN DE USUARIOS
# ============================================================================

@router.post("/registro")
async def registrar_usuario(
    usuario_data: UserRegistration, 
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Registra nuevo usuario con validaciones de seguridad híbrida (PIN o contraseña segura) y deja inactivo hasta activación por email."""
    client_info = get_client_info(request)
    logger.info(f"Intento de registro: usuario={sanitize_for_log(usuario_data.usuario)}, email={sanitize_for_log(usuario_data.mail)}")
    try:
        # Validar email
        if not validar_email(usuario_data.mail):
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "invalid_email",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    "email": sanitize_for_log(usuario_data.mail),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El email no es válido"
            )
        # Verificar si el usuario ya existe
        existing_user = get_usuario(db, usuario=usuario_data.usuario)
        if existing_user:
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "user_exists",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El nombre de usuario ya está en uso"
            )
        # VALIDACIÓN HÍBRIDA: PIN o contraseña segura
        validation_result = validate_password(usuario_data.clave)
        if not validation_result["valid"]:
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "invalid_password",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    "password_type": validation_result.get("type", "unknown"),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=validation_result["message"]
            )
        # Log tipo de autenticación seleccionado
        auth_type = "PIN" if validation_result.get("type") == "pin" else "Contraseña Segura"
        logger.info(f"Usuario {sanitize_for_log(usuario_data.usuario)} registrado con {auth_type}")
        # Encriptar contraseña
        clave_encriptada = encriptar_clave(usuario_data.clave)
        # Crear usuario INACTIVO
        result = create_usuario(
            db=db,
            nombre=usuario_data.nombre,
            usuario=usuario_data.usuario,
            clave=clave_encriptada,
            mail=usuario_data.mail,
            activo=False  # <-- usuario inactivo hasta activación
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creando usuario"
            )
        # Crear token de activación
        token_activacion = crear_access_token(
            data={"sub": usuario_data.usuario, "type": "activation"},
            expires_delta=activation_token_expires
        )
        # Enviar email de activación
        try:
            if validar_email(usuario_data.mail):
                activation_link = f"{BASE_URL}/user/activar-cuenta?token={token_activacion}"
                background_tasks.add_task(
                    enviar_email_simple,
                    usuario_data.mail,
                    "Activa tu cuenta",
                    f"""
                    Bienvenido/a {usuario_data.nombre},\n\nPor favor activa tu cuenta haciendo clic en el siguiente enlace:\n{activation_link}\n\nEste enlace expira en 24 horas.\n\nSi no solicitaste esto, ignora este mensaje.
                    """
                )
                logger.info(f"Email de activación enviado a {sanitize_for_log(usuario_data.mail)}")
        except Exception as e:
            logger.warning(f"Error validando/enviando email de activación: {str(e)}")
        log_security_event(
            "USER_REGISTERED",
            {
                "usuario": sanitize_for_log(usuario_data.usuario),
                "email": sanitize_for_log(usuario_data.mail),
                **client_info
            },
            "INFO"
        )
        return JSONResponse(
            content={
                "message": "Usuario registrado exitosamente. Revisa tu email para activar la cuenta.",
                "usuario": usuario_data.usuario,
                "activacion_requerida": True
            },
            status_code=status.HTTP_201_CREATED
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en registro: {str(e)}")
        log_security_event(
            "REGISTRATION_ERROR",
            {"error": str(e), **client_info},
            "ERROR"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

# Endpoint de activación de cuenta
from fastapi import Query

@router.get("/activar-cuenta")
async def activar_cuenta(token: str = Query(...), db: Session = Depends(get_db)):
    """Activa la cuenta de usuario usando el token enviado por email."""
    try:
        payload = jwt.decode(token, SECRET.key, algorithms=[ALGORITHM])
        username = payload.get("sub")
        token_type = payload.get("type")
        if not username or token_type != "activation":
            raise HTTPException(status_code=400, detail="Token inválido")
        user = db.query(UsuariosModel).filter(UsuariosModel.usuario == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        if user.activo:
            return {"message": "La cuenta ya está activada"}
        user.activo = True
        db.commit()
        log_security_event(
            "USER_ACTIVATED",
            {"usuario": sanitize_for_log(username)},
            "INFO"
        )
        return {"message": "Cuenta activada exitosamente. Ya puedes iniciar sesión."}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="El enlace de activación ha expirado")
    except Exception as e:
        log_security_event(
            "USER_ACTIVATION_ERROR",
            {"error": str(e)},
            "ERROR"
        )
        raise HTTPException(status_code=400, detail="Token inválido o error de activación")

# ============================================================================
# RUTAS DE GESTIÓN DE USUARIOS
# ============================================================================

@router.post("/registro")
async def registrar_usuario(
    usuario_data: UserRegistration, 
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Registra nuevo usuario con validaciones de seguridad híbrida (PIN o contraseña segura) y deja inactivo hasta activación por email."""
    client_info = get_client_info(request)
    logger.info(f"Intento de registro: usuario={sanitize_for_log(usuario_data.usuario)}, email={sanitize_for_log(usuario_data.mail)}")
    try:
        # Validar email
        if not validar_email(usuario_data.mail):
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "invalid_email",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    "email": sanitize_for_log(usuario_data.mail),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El email no es válido"
            )
        # Verificar si el usuario ya existe
        existing_user = get_usuario(db, usuario=usuario_data.usuario)
        if existing_user:
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "user_exists",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El nombre de usuario ya está en uso"
            )
        # VALIDACIÓN HÍBRIDA: PIN o contraseña segura
        validation_result = validate_password(usuario_data.clave)
        if not validation_result["valid"]:
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "invalid_password",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    "password_type": validation_result.get("type", "unknown"),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=validation_result["message"]
            )
        # Log tipo de autenticación seleccionado
        auth_type = "PIN" if validation_result.get("type") == "pin" else "Contraseña Segura"
        logger.info(f"Usuario {sanitize_for_log(usuario_data.usuario)} registrado con {auth_type}")
        # Encriptar contraseña
        clave_encriptada = encriptar_clave(usuario_data.clave)
        # Crear usuario INACTIVO
        result = create_usuario(
            db=db,
            nombre=usuario_data.nombre,
            usuario=usuario_data.usuario,
            clave=clave_encriptada,
            mail=usuario_data.mail,
            activo=False  # <-- usuario inactivo hasta activación
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creando usuario"
            )
        # Crear token de activación
        token_activacion = crear_access_token(
            data={"sub": usuario_data.usuario, "type": "activation"},
            expires_delta=activation_token_expires
        )
        # Enviar email de activación
        try:
            if validar_email(usuario_data.mail):
                activation_link = f"{BASE_URL}/user/activar-cuenta?token={token_activacion}"
                background_tasks.add_task(
                    enviar_email_simple,
                    usuario_data.mail,
                    "Activa tu cuenta",
                    f"""
                    Bienvenido/a {usuario_data.nombre},\n\nPor favor activa tu cuenta haciendo clic en el siguiente enlace:\n{activation_link}\n\nEste enlace expira en 24 horas.\n\nSi no solicitaste esto, ignora este mensaje.
                    """
                )
                logger.info(f"Email de activación enviado a {sanitize_for_log(usuario_data.mail)}")
        except Exception as e:
            logger.warning(f"Error validando/enviando email de activación: {str(e)}")
        log_security_event(
            "USER_REGISTERED",
            {
                "usuario": sanitize_for_log(usuario_data.usuario),
                "email": sanitize_for_log(usuario_data.mail),
                **client_info
            },
            "INFO"
        )
        return JSONResponse(
            content={
                "message": "Usuario registrado exitosamente. Revisa tu email para activar la cuenta.",
                "usuario": usuario_data.usuario,
                "activacion_requerida": True
            },
            status_code=status.HTTP_201_CREATED
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en registro: {str(e)}")
        log_security_event(
            "REGISTRATION_ERROR",
            {"error": str(e), **client_info},
            "ERROR"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

# Endpoint de activación de cuenta
from fastapi import Query

@router.get("/activar-cuenta")
async def activar_cuenta(token: str = Query(...), db: Session = Depends(get_db)):
    """Activa la cuenta de usuario usando el token enviado por email."""
    try:
        payload = jwt.decode(token, SECRET.key, algorithms=[ALGORITHM])
        username = payload.get("sub")
        token_type = payload.get("type")
        if not username or token_type != "activation":
            raise HTTPException(status_code=400, detail="Token inválido")
        user = db.query(UsuariosModel).filter(UsuariosModel.usuario == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        if user.activo:
            return {"message": "La cuenta ya está activada"}
        user.activo = True
        db.commit()
        log_security_event(
            "USER_ACTIVATED",
            {"usuario": sanitize_for_log(username)},
            "INFO"
        )
        return {"message": "Cuenta activada exitosamente. Ya puedes iniciar sesión."}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="El enlace de activación ha expirado")
    except Exception as e:
        log_security_event(
            "USER_ACTIVATION_ERROR",
            {"error": str(e)},
            "ERROR"
        )
        raise HTTPException(status_code=400, detail="Token inválido o error de activación")

# ============================================================================
# RUTAS DE GESTIÓN DE USUARIOS
# ============================================================================

@router.post("/registro")
async def registrar_usuario(
    usuario_data: UserRegistration, 
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Registra nuevo usuario con validaciones de seguridad híbrida (PIN o contraseña segura) y deja inactivo hasta activación por email."""
    client_info = get_client_info(request)
    logger.info(f"Intento de registro: usuario={sanitize_for_log(usuario_data.usuario)}, email={sanitize_for_log(usuario_data.mail)}")
    try:
        # Validar email
        if not validar_email(usuario_data.mail):
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "invalid_email",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    "email": sanitize_for_log(usuario_data.mail),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El email no es válido"
            )
        # Verificar si el usuario ya existe
        existing_user = get_usuario(db, usuario=usuario_data.usuario)
        if existing_user:
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "user_exists",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El nombre de usuario ya está en uso"
            )
        # VALIDACIÓN HÍBRIDA: PIN o contraseña segura
        validation_result = validate_password(usuario_data.clave)
        if not validation_result["valid"]:
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "invalid_password",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    "password_type": validation_result.get("type", "unknown"),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=validation_result["message"]
            )
        # Log tipo de autenticación seleccionado
        auth_type = "PIN" if validation_result.get("type") == "pin" else "Contraseña Segura"
        logger.info(f"Usuario {sanitize_for_log(usuario_data.usuario)} registrado con {auth_type}")
        # Encriptar contraseña
        clave_encriptada = encriptar_clave(usuario_data.clave)
        # Crear usuario INACTIVO
        result = create_usuario(
            db=db,
            nombre=usuario_data.nombre,
            usuario=usuario_data.usuario,
            clave=clave_encriptada,
            mail=usuario_data.mail,
            activo=False  # <-- usuario inactivo hasta activación
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creando usuario"
            )
        # Crear token de activación
        token_activacion = crear_access_token(
            data={"sub": usuario_data.usuario, "type": "activation"},
            expires_delta=activation_token_expires
        )
        # Enviar email de activación
        try:
            if validar_email(usuario_data.mail):
                activation_link = f"{BASE_URL}/user/activar-cuenta?token={token_activacion}"
                background_tasks.add_task(
                    enviar_email_simple,
                    usuario_data.mail,
                    "Activa tu cuenta",
                    f"""
                    Bienvenido/a {usuario_data.nombre},\n\nPor favor activa tu cuenta haciendo clic en el siguiente enlace:\n{activation_link}\n\nEste enlace expira en 24 horas.\n\nSi no solicitaste esto, ignora este mensaje.
                    """
                )
                logger.info(f"Email de activación enviado a {sanitize_for_log(usuario_data.mail)}")
        except Exception as e:
            logger.warning(f"Error validando/enviando email de activación: {str(e)}")
        log_security_event(
            "USER_REGISTERED",
            {
                "usuario": sanitize_for_log(usuario_data.usuario),
                "email": sanitize_for_log(usuario_data.mail),
                **client_info
            },
            "INFO"
        )
        return JSONResponse(
            content={
                "message": "Usuario registrado exitosamente. Revisa tu email para activar la cuenta.",
                "usuario": usuario_data.usuario,
                "activacion_requerida": True
            },
            status_code=status.HTTP_201_CREATED
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en registro: {str(e)}")
        log_security_event(
            "REGISTRATION_ERROR",
            {"error": str(e), **client_info},
            "ERROR"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

# Endpoint de activación de cuenta
from fastapi import Query

@router.get("/activar-cuenta")
async def activar_cuenta(token: str = Query(...), db: Session = Depends(get_db)):
    """Activa la cuenta de usuario usando el token enviado por email."""
    try:
        payload = jwt.decode(token, SECRET.key, algorithms=[ALGORITHM])
        username = payload.get("sub")
        token_type = payload.get("type")
        if not username or token_type != "activation":
            raise HTTPException(status_code=400, detail="Token inválido")
        user = db.query(UsuariosModel).filter(UsuariosModel.usuario == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        if user.activo:
            return {"message": "La cuenta ya está activada"}
        user.activo = True
        db.commit()
        log_security_event(
            "USER_ACTIVATED",
            {"usuario": sanitize_for_log(username)},
            "INFO"
        )
        return {"message": "Cuenta activada exitosamente. Ya puedes iniciar sesión."}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="El enlace de activación ha expirado")
    except Exception as e:
        log_security_event(
            "USER_ACTIVATION_ERROR",
            {"error": str(e)},
            "ERROR"
        )
        raise HTTPException(status_code=400, detail="Token inválido o error de activación")

# ============================================================================
# RUTAS DE GESTIÓN DE USUARIOS
# ============================================================================

@router.post("/registro")
async def registrar_usuario(
    usuario_data: UserRegistration, 
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Registra nuevo usuario con validaciones de seguridad híbrida (PIN o contraseña segura) y deja inactivo hasta activación por email."""
    client_info = get_client_info(request)
    logger.info(f"Intento de registro: usuario={sanitize_for_log(usuario_data.usuario)}, email={sanitize_for_log(usuario_data.mail)}")
    try:
        # Validar email
        if not validar_email(usuario_data.mail):
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "invalid_email",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    "email": sanitize_for_log(usuario_data.mail),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El email no es válido"
            )
        # Verificar si el usuario ya existe
        existing_user = get_usuario(db, usuario=usuario_data.usuario)
        if existing_user:
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "user_exists",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El nombre de usuario ya está en uso"
            )
        # VALIDACIÓN HÍBRIDA: PIN o contraseña segura
        validation_result = validate_password(usuario_data.clave)
        if not validation_result["valid"]:
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "invalid_password",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    "password_type": validation_result.get("type", "unknown"),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=validation_result["message"]
            )
        # Log tipo de autenticación seleccionado
        auth_type = "PIN" if validation_result.get("type") == "pin" else "Contraseña Segura"
        logger.info(f"Usuario {sanitize_for_log(usuario_data.usuario)} registrado con {auth_type}")
        # Encriptar contraseña
        clave_encriptada = encriptar_clave(usuario_data.clave)
        # Crear usuario INACTIVO
        result = create_usuario(
            db=db,
            nombre=usuario_data.nombre,
            usuario=usuario_data.usuario,
            clave=clave_encriptada,
            mail=usuario_data.mail,
            activo=False  # <-- usuario inactivo hasta activación
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creando usuario"
            )
        # Crear token de activación
        token_activacion = crear_access_token(
            data={"sub": usuario_data.usuario, "type": "activation"},
            expires_delta=activation_token_expires
        )
        # Enviar email de activación
        try:
            if validar_email(usuario_data.mail):
                activation_link = f"{BASE_URL}/user/activar-cuenta?token={token_activacion}"
                background_tasks.add_task(
                    enviar_email_simple,
                    usuario_data.mail,
                    "Activa tu cuenta",
                    f"""
                    Bienvenido/a {usuario_data.nombre},\n\nPor favor activa tu cuenta haciendo clic en el siguiente enlace:\n{activation_link}\n\nEste enlace expira en 24 horas.\n\nSi no solicitaste esto, ignora este mensaje.
                    """
                )
                logger.info(f"Email de activación enviado a {sanitize_for_log(usuario_data.mail)}")
        except Exception as e:
            logger.warning(f"Error validando/enviando email de activación: {str(e)}")
        log_security_event(
            "USER_REGISTERED",
            {
                "usuario": sanitize_for_log(usuario_data.usuario),
                "email": sanitize_for_log(usuario_data.mail),
                **client_info
            },
            "INFO"
        )
        return JSONResponse(
            content={
                "message": "Usuario registrado exitosamente. Revisa tu email para activar la cuenta.",
                "usuario": usuario_data.usuario,
                "activacion_requerida": True
            },
            status_code=status.HTTP_201_CREATED
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en registro: {str(e)}")
        log_security_event(
            "REGISTRATION_ERROR",
            {"error": str(e), **client_info},
            "ERROR"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

# Endpoint de activación de cuenta
from fastapi import Query

@router.get("/activar-cuenta")
async def activar_cuenta(token: str = Query(...), db: Session = Depends(get_db)):
    """Activa la cuenta de usuario usando el token enviado por email."""
    try:
        payload = jwt.decode(token, SECRET.key, algorithms=[ALGORITHM])
        username = payload.get("sub")
        token_type = payload.get("type")
        if not username or token_type != "activation":
            raise HTTPException(status_code=400, detail="Token inválido")
        user = db.query(UsuariosModel).filter(UsuariosModel.usuario == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        if user.activo:
            return {"message": "La cuenta ya está activada"}
        user.activo = True
        db.commit()
        log_security_event(
            "USER_ACTIVATED",
            {"usuario": sanitize_for_log(username)},
            "INFO"
        )
        return {"message": "Cuenta activada exitosamente. Ya puedes iniciar sesión."}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="El enlace de activación ha expirado")
    except Exception as e:
        log_security_event(
            "USER_ACTIVATION_ERROR",
            {"error": str(e)},
            "ERROR"
        )
        raise HTTPException(status_code=400, detail="Token inválido o error de activación")

# ============================================================================
# RUTAS DE GESTIÓN DE USUARIOS
# ============================================================================

@router.post("/registro")
async def registrar_usuario(
    usuario_data: UserRegistration, 
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Registra nuevo usuario con validaciones de seguridad híbrida (PIN o contraseña segura) y deja inactivo hasta activación por email."""
    client_info = get_client_info(request)
    logger.info(f"Intento de registro: usuario={sanitize_for_log(usuario_data.usuario)}, email={sanitize_for_log(usuario_data.mail)}")
    try:
        # Validar email
        if not validar_email(usuario_data.mail):
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "invalid_email",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    "email": sanitize_for_log(usuario_data.mail),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El email no es válido"
            )
        # Verificar si el usuario ya existe
        existing_user = get_usuario(db, usuario=usuario_data.usuario)
        if existing_user:
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "user_exists",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El nombre de usuario ya está en uso"
            )
        # VALIDACIÓN HÍBRIDA: PIN o contraseña segura
        validation_result = validate_password(usuario_data.clave)
        if not validation_result["valid"]:
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "invalid_password",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    "password_type": validation_result.get("type", "unknown"),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=validation_result["message"]
            )
        # Log tipo de autenticación seleccionado
        auth_type = "PIN" if validation_result.get("type") == "pin" else "Contraseña Segura"
        logger.info(f"Usuario {sanitize_for_log(usuario_data.usuario)} registrado con {auth_type}")
        # Encriptar contraseña
        clave_encriptada = encriptar_clave(usuario_data.clave)
        # Crear usuario INACTIVO
        result = create_usuario(
            db=db,
            nombre=usuario_data.nombre,
            usuario=usuario_data.usuario,
            clave=clave_encriptada,
            mail=usuario_data.mail,
            activo=False  # <-- usuario inactivo hasta activación
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creando usuario"
            )
        # Crear token de activación
        token_activacion = crear_access_token(
            data={"sub": usuario_data.usuario, "type": "activation"},
            expires_delta=activation_token_expires
        )
        # Enviar email de activación
        try:
            if validar_email(usuario_data.mail):
                activation_link = f"{BASE_URL}/user/activar-cuenta?token={token_activacion}"
                background_tasks.add_task(
                    enviar_email_simple,
                    usuario_data.mail,
                    "Activa tu cuenta",
                    f"""
                    Bienvenido/a {usuario_data.nombre},\n\nPor favor activa tu cuenta haciendo clic en el siguiente enlace:\n{activation_link}\n\nEste enlace expira en 24 horas.\n\nSi no solicitaste esto, ignora este mensaje.
                    """
                )
                logger.info(f"Email de activación enviado a {sanitize_for_log(usuario_data.mail)}")
        except Exception as e:
            logger.warning(f"Error validando/enviando email de activación: {str(e)}")
        log_security_event(
            "USER_REGISTERED",
            {
                "usuario": sanitize_for_log(usuario_data.usuario),
                "email": sanitize_for_log(usuario_data.mail),
                **client_info
            },
            "INFO"
        )
        return JSONResponse(
            content={
                "message": "Usuario registrado exitosamente. Revisa tu email para activar la cuenta.",
                "usuario": usuario_data.usuario,
                "activacion_requerida": True
            },
            status_code=status.HTTP_201_CREATED
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en registro: {str(e)}")
        log_security_event(
            "REGISTRATION_ERROR",
            {"error": str(e), **client_info},
            "ERROR"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

# Endpoint de activación de cuenta
from fastapi import Query

@router.get("/activar-cuenta")
async def activar_cuenta(token: str = Query(...), db: Session = Depends(get_db)):
    """Activa la cuenta de usuario usando el token enviado por email."""
    try:
        payload = jwt.decode(token, SECRET.key, algorithms=[ALGORITHM])
        username = payload.get("sub")
        token_type = payload.get("type")
        if not username or token_type != "activation":
            raise HTTPException(status_code=400, detail="Token inválido")
        user = db.query(UsuariosModel).filter(UsuariosModel.usuario == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        if user.activo:
            return {"message": "La cuenta ya está activada"}
        user.activo = True
        db.commit()
        log_security_event(
            "USER_ACTIVATED",
            {"usuario": sanitize_for_log(username)},
            "INFO"
        )
        return {"message": "Cuenta activada exitosamente. Ya puedes iniciar sesión."}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="El enlace de activación ha expirado")
    except Exception as e:
        log_security_event(
            "USER_ACTIVATION_ERROR",
            {"error": str(e)},
            "ERROR"
        )
        raise HTTPException(status_code=400, detail="Token inválido o error de activación")

# ============================================================================
# RUTAS DE GESTIÓN DE USUARIOS
# ============================================================================

@router.post("/registro")
async def registrar_usuario(
    usuario_data: UserRegistration, 
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Registra nuevo usuario con validaciones de seguridad híbrida (PIN o contraseña segura) y deja inactivo hasta activación por email."""
    client_info = get_client_info(request)
    logger.info(f"Intento de registro: usuario={sanitize_for_log(usuario_data.usuario)}, email={sanitize_for_log(usuario_data.mail)}")
    try:
        # Validar email
        if not validar_email(usuario_data.mail):
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "invalid_email",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    "email": sanitize_for_log(usuario_data.mail),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El email no es válido"
            )
        # Verificar si el usuario ya existe
        existing_user = get_usuario(db, usuario=usuario_data.usuario)
        if existing_user:
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "user_exists",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El nombre de usuario ya está en uso"
            )
        # VALIDACIÓN HÍBRIDA: PIN o contraseña segura
        validation_result = validate_password(usuario_data.clave)
        if not validation_result["valid"]:
            log_security_event(
                "REGISTRATION_FAILED",
                {
                    "reason": "invalid_password",
                    "usuario": sanitize_for_log(usuario_data.usuario),
                    "password_type": validation_result.get("type", "unknown"),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=validation_result["message"]
            )
        # Log tipo de autenticación seleccionado
        auth_type = "PIN" if validation_result.get("type") == "pin" else "Contraseña Segura"
        logger.info(f"Usuario {sanitize_for_log(usuario_data.usuario)} registrado con {auth_type}")
        # Encriptar contraseña
        clave_encriptada = encriptar_clave(usuario_data.clave)
        # Crear usuario INACTIVO
        result = create_usuario(
            db=db,
            nombre=usuario_data.nombre,
            usuario=usuario_data.usuario,
            clave=clave_encriptada,
            mail=usuario_data.mail,
            activo=False  # <-- usuario inactivo hasta activación
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creando usuario"
            )
        # Crear token de activación
        token_activacion = crear_access_token(
            data={"sub": usuario_data.usuario, "type": "activation"},
            expires_delta=activation_token_expires
        )
        # Enviar email de activación
        try:
            if validar_email(usuario_data.mail):
                activation_link = f"{BASE_URL}/user/activar-cuenta?token={token_activacion}"
                background_tasks.add_task(
                    enviar_email_simple,
                    usuario_data.mail,
                    "Activa tu cuenta",
                    f"""
                    Bienvenido/a {usuario_data.nombre},\n\nPor favor activa tu cuenta haciendo clic en el siguiente enlace:\n{activation_link}\n\nEste enlace expira en 24 horas.\n\nSi no solicitaste esto, ignora este mensaje.
                    """
                )
                logger.info(f"Email de activación enviado a {sanitize_for_log(usuario_data.mail)}")
        except Exception as e:
            logger.warning(f"Error validando/enviando email de activación: {str(e)}")
        log_security_event(
            "USER_REGISTERED",
            {
                "usuario": sanitize_for_log(usuario_data.usuario),
                "email": sanitize_for_log(usuario_data.mail),
                **client_info
            },
            "INFO"
        )
        return JSONResponse(
            content={
                "message": "Usuario registrado exitosamente. Revisa tu email para activar la cuenta.",
                "usuario": usuario_data.usuario,
                "activacion_requerida": True
            },
            status_code=status.HTTP_201_CREATED
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en registro: {str(e)}")
        log_security_event(
            "REGISTRATION_ERROR",
            {"error": str(e), **client_info},
            "ERROR"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

# ============================================================================
# RUTAS DE ADMINISTRACIÓN DE USUARIOS (Solo para administradores)
# ============================================================================

@router.get("/admin/lista")
async def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    user: UsuariosModel = Depends(get_current_user_secure),
    db: Session = Depends(get_db)
):
    """Listar usuarios (solo administradores)"""
    try:
        # Verificar si el usuario es administrador
        if not hasattr(user, 'roles') or not any(
            role.nombre.lower() == 'admin' or role.nombre.lower() == 'administrador' 
            for role in user.roles
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para acceder a esta funcionalidad"
            )
          # Obtener lista de usuarios
        usuarios = gets_usuarios(db)
        
        # Formatear respuesta excluyendo información sensible
        usuarios_response = []
        for usuario in usuarios:
            user_data = {
                "codigo": usuario.codigo,
                "usuario": usuario.usuario,
                "nombre": usuario.nombre,
                "email": usuario.mail,
                "activo": usuario.activo,
                "fecha_creacion": usuario.fecha_creacion.isoformat() if hasattr(usuario, 'fecha_creacion') and user.fecha_creacion else None,
                "ultimo_acceso": usuario.ultimo_acceso.isoformat() if hasattr(usuario, 'ultimo_acceso') and user.ultimo_acceso else None
            }
            
            # Incluir roles si están disponibles
            if hasattr(usuario, "roles") and usuario.roles:
                user_data["roles"] = [
                    {
                        "id": role.id if hasattr(role, 'id') else 0,
                        "nombre": role.nombre if hasattr(role, 'nombre') else str(role)
                    }
                    for role in usuario.roles
                ]
            else:
                user_data["roles"] = []
            
            usuarios_response.append(user_data)
        
        return {
            "usuarios": usuarios_response,
            "total": len(usuarios_response),
            "skip": skip,
            "limit": limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listando usuarios: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno listando usuarios"
        )

@router.get("/admin/{usuario_id}")
async def obtener_usuario_admin(
    usuario_id: int,
    user: UsuariosModel = Depends(get_current_user_secure),
    db: Session = Depends(get_db)
):
    """Obtener información de un usuario específico (solo administradores)"""
    try:
        # Verificar si el usuario es administrador
        if not hasattr(user, 'roles') or not any(
            role.nombre.lower() == 'admin' or role.nombre.lower() == 'administrador' 
            for role in user.roles
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para acceder a esta funcionalidad"
            )
        
        # Obtener usuario por ID
        usuario = get_usuario(db, usuario_id=usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Formatear respuesta
        user_data = {
            "codigo": usuario.codigo,
            "usuario": usuario.usuario,
            "nombre": usuario.nombre,
            "email": usuario.mail,
            "activo": usuario.activo,
            "fecha_creacion": usuario.fecha_creacion.isoformat() if hasattr(usuario, 'fecha_creacion') and user.fecha_creacion else None,
            "ultimo_acceso": usuario.ultimo_acceso.isoformat() if hasattr(usuario, 'ultimo_acceso') and user.ultimo_acceso else None
        }
        
        # Incluir roles si están disponibles
        if hasattr(usuario, "roles") and usuario.roles:
            user_data["roles"] = [
                {
                    "id": role.id if hasattr(role, 'id') else 0,
                    "nombre": role.nombre if hasattr(role, 'nombre') else str(role),
                    "descripcion": role.descripcion if hasattr(role, 'descripcion') else ""
                }
                for role in usuario.roles
            ]
        else:
            user_data["roles"] = []
        
        return user_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno obteniendo usuario"
        )

# ============================================================================
# RUTAS PARA RESTABLECIMIENTO DE CONTRASEÑA
# ============================================================================

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
    """Solicita reset de contraseña con protecciones de seguridad y solo para usuarios ACTIVOS."""
    client_info = get_client_info(request)
    client_ip = client_info.get("ip", "unknown")
    try:
        # Rate limiting para reset requests
        current_time = datetime.now()
        if client_ip in reset_attempts:
            attempts = reset_attempts[client_ip]
            attempts = [t for t in attempts if (current_time - t).seconds < 3600]
            reset_attempts[client_ip] = attempts
            if len(attempts) >= max_reset_attempts:
                log_security_event(
                    "PASSWORD_RESET_RATE_LIMITED",
                    {"email": sanitize_for_log(request_data.email), **client_info},
                    "WARNING"
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Demasiados intentos de reset. Intente en 1 hora"
                )
        # Buscar usuario ACTIVO
        user = db.query(UsuariosModel).filter(
            UsuariosModel.mail == request_data.email,
            UsuariosModel.activo == True
        ).first()
        if user:
            reset_token = crear_access_token(
                data={
                    "sub": user.usuario,
                    "type": "password_reset",
                    "email": request_data.email
                },
                expires_delta=password_reset_expires
            )
            reset_link = f"{BASE_URL}/confirm-password-reset?token={reset_token}"
            message = f"""
            Solicitud de restablecimiento de contraseña.\n\nSi solicitaste restablecer tu contraseña, haz clic en el siguiente enlace:\n{reset_link}\n\nEste enlace expira en 1 hora.\n\nSi no solicitaste esto, ignora este mensaje.
            """
            background_tasks.add_task(
                enviar_email_simple,
                request_data.email,
                "Restablecimiento de contraseña",
                message
            )
        if client_ip not in reset_attempts:
            reset_attempts[client_ip] = []
        reset_attempts[client_ip].append(current_time)
        log_security_event(
            "PASSWORD_RESET_REQUESTED",
            {"email": sanitize_for_log(request_data.email), **client_info},
            "INFO"
        )
        return {
            "message": "Si el correo está registrado y activo, recibirás instrucciones para restablecer tu contraseña"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en password reset request: {str(e)}")
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
    db: Session = Depends(get_db)
):
    """Confirma el reset de contraseña con token y nueva contraseña (solo usuarios ACTIVOS, validación fuerte)."""
    client_info = get_client_info(request)
    try:
        try:
            payload = jwt.decode(reset_data.token, SECRET.key, algorithms=[ALGORITHM])
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
                detail="Token expirado"
            )
        except JWTError:
            log_security_event(
                "PASSWORD_RESET_INVALID_TOKEN",
                {"token": sanitize_for_log(reset_data.token[:20]), **client_info},
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido"
            )
        except Exception as e:
            log_security_event(
                "PASSWORD_RESET_TOKEN_ERROR",
                {"token": sanitize_for_log(reset_data.token[:20]), "error": str(e), **client_info},
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido o expirado"
            )
        # Buscar usuario ACTIVO
        user = db.query(UsuariosModel).filter(UsuariosModel.usuario == username, UsuariosModel.activo == True).first()
        if not user:
            log_security_event(
                "PASSWORD_RESET_USER_NOT_FOUND_OR_INACTIVE",
                {"username": sanitize_for_log(username), **client_info},
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido o usuario inactivo"
            )
        if email and user.mail != email:
            log_security_event(
                "PASSWORD_RESET_EMAIL_MISMATCH",
                {"username": sanitize_for_log(username), "expected_email": sanitize_for_log(email), **client_info},
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido o expirado"
            )
        if reset_data.new_password != reset_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las contraseñas no coinciden"
            )
        # Validar seguridad de la nueva contraseña
        validation_result = validate_password(reset_data.new_password)
        if not validation_result["valid"]:
            log_security_event(
                "PASSWORD_RESET_FAILED",
                {
                    "username": sanitize_for_log(username),
                    "reason": "invalid_new_password",
                    "password_type": validation_result.get("type", "unknown"),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=validation_result["message"]
            )
        # Bloquear si la nueva contraseña es igual a la anterior
        if verify_password(reset_data.new_password, user.clave):
            log_security_event(
                "PASSWORD_RESET_FAILED",
                {
                    "username": sanitize_for_log(username),
                    "reason": "same_as_old_password",
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña no puede ser igual a la anterior"
            )
        new_password_hash = encriptar_clave(reset_data.new_password)
        user.clave = new_password_hash
        db.commit()
        log_security_event(
            "PASSWORD_RESET_COMPLETED",
            {"username": sanitize_for_log(username), "user_id": user.codigo, **client_info},
            "INFO"
        )
        try:
            enviar_email_simple(
                user.mail,
                "Contraseña cambiada exitosamente",
                f"""
                Hola {user.nombre},\n\nTu contraseña ha sido cambiada exitosamente.\n\nSi no realizaste esta acción, por favor contacta inmediatamente con soporte.
                """
            )
        except Exception:
            pass
        return {
            "message": "Contraseña actualizada exitosamente",
            "success": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en confirm password reset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno procesando solicitud"
        )

# ============================================================================
# RUTA DE VERIFICACIÓN DE SALUD
# ============================================================================

@router.get("/health")
async def health_check():
    """Verificar que el router de usuarios está funcionando"""
    return {
        "status": "ok",
        "service": "usuarios",
        "timestamp": datetime.now().isoformat(),
        "routes": [
            "POST /user/registro - Registrar nuevo usuario",
            "GET /user/perfil - Obtener perfil del usuario",
            "PUT /user/perfil - Actualizar perfil del usuario", 
            "POST /user/cambiar-password - Cambiar contraseña",
            "GET /reset-password - Página para solicitar recuperación de contraseña",
            "POST /password-reset-request - Solicitar recuperación de contraseña",
            "GET /confirm-password-reset - Página para confirmar nueva contraseña",
            "POST /confirm-password-reset - Confirmar nueva contraseña",
            "GET /user/roles - Obtener roles del usuario",
            "GET /user/admin/lista - Listar usuarios (admin)",
            "GET /user/admin/{usuario_id} - Obtener usuario (admin)"
        ]
    }

class AdminPasswordChange(BaseModel):
    nueva_password: str

@router.put("/admin/cambiar-password")
async def cambiar_password_admin(
    password_data: AdminPasswordChange,
    request: Request,
    user: UsuariosModel = Depends(get_current_user_secure),
    db: Session = Depends(get_db)
):
    """Cambia la contraseña del usuario admin (solo para administradores autenticados)."""
    client_info = get_client_info(request)
    try:
        # Verificar si el usuario autenticado es admin
        if not hasattr(user, 'roles') or not any(
            role.nombre.lower() == 'admin' or role.nombre.lower() == 'administrador'
            for role in user.roles
        ):
            log_security_event(
                "ADMIN_PASSWORD_CHANGE_DENIED",
                {"usuario": sanitize_for_log(user.usuario), **client_info},
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para cambiar la contraseña del usuario admin"
            )

        # Buscar al usuario admin
        admin_user = db.query(UsuariosModel).filter(UsuariosModel.usuario == "admin").first()
        if not admin_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario admin no encontrado"
            )

        # Validar seguridad de la nueva contraseña
        validation_result = validate_password(password_data.nueva_password)
        if not validation_result["valid"]:
            log_security_event(
                "ADMIN_PASSWORD_CHANGE_FAILED",
                {
                    "usuario": sanitize_for_log(user.usuario),
                    "reason": "invalid_password",
                    "password_type": validation_result.get("type", "unknown"),
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=validation_result["message"]
            )

        # Bloquear si la nueva contraseña es igual a la anterior
        if verify_password(password_data.nueva_password, admin_user.clave):
            log_security_event(
                "ADMIN_PASSWORD_CHANGE_FAILED",
                {
                    "usuario": sanitize_for_log(user.usuario),
                    "reason": "same_as_old_password",
                    **client_info
                },
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña no puede ser igual a la anterior"
            )

        # Encriptar la nueva contraseña
        nueva_password_encriptada = encriptar_clave(password_data.nueva_password)

        # Actualizar la contraseña
        admin_user.clave = nueva_password_encriptada
        db.commit()

        log_security_event(
            "ADMIN_PASSWORD_CHANGED",
            {
                "usuario": sanitize_for_log(user.usuario),
                "admin_user": "admin",
                **client_info
            },
            "INFO"
        )

        return {"message": "Contraseña del usuario admin actualizada exitosamente"}

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        log_security_event(
            "ADMIN_PASSWORD_CHANGE_ERROR",
            {"error": str(e), **client_info},
            "ERROR"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar la contraseña: {str(e)}"
        )
