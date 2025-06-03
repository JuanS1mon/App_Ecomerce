"""
Router de usuarios mejorado con seguridad avanzada
Incluye validaciones robustas, logging seguro y protección contra ataques
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status, BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, validator, Field
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from datetime import timedelta, datetime
import logging
import secrets
import re
from typing import Optional

# Importar versiones mejoradas de seguridad
from Services.security.security_improved import (
    ACCESS_TOKEN_DURATION, 
    authenticate_user, 
    current_user, 
    encriptar_clave, 
    verificar_clave, 
    crear_access_token,
    decodifica_token,
    validate_username,
    validate_password_strength,
    log_security_event,
    revoke_token
)

from Services.mail.mail import enviar_correo, validar_email
from Services.comunicacion.whassap import enviar_mensaje_whatsapp, validar_telefono

from db.crud.config.Usuarios import (
    get_usuario, 
    create_usuario, 
    update_usuario_activate
)
from db.database import get_db
from db.schemas.config.Usuarios import (
    UserDB, 
    PasswordReset, 
    PasswordResetRequest
)
from db.models.config.usuarios import usuarios as UsuariosModel

from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

# Configuración del router
router = APIRouter(
    include_in_schema=False,
    tags=["usuario"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

# Configuración de logging seguro
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()
BASE_URL = os.getenv("BASE_URL")

if not BASE_URL:
    raise ValueError("BASE_URL no configurado en variables de entorno")

# Configuración de seguridad
activation_token_expires = timedelta(minutes=15)  # Reducido de 10 a 15 minutos
password_reset_expires = timedelta(hours=1)  # Token de reset expira en 1 hora
max_reset_attempts = 3  # Máximo intentos de reset por hora

# Configurar Jinja2Templates
templates = Jinja2Templates(directory="static")

# Modelos mejorados con validación
class UserRegistration(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre completo")
    usuario: str = Field(..., min_length=3, max_length=30, description="Nombre de usuario")
    clave: str = Field(..., min_length=8, max_length=128, description="Contraseña")
    mail: EmailStr = Field(..., description="Correo electrónico")
    telefono: Optional[str] = Field(None, min_length=10, max_length=15, description="Teléfono")
    acepta_terminos: bool = Field(..., description="Aceptación de términos y condiciones")
    
    @validator('nombre')
    def validate_nombre(cls, v):
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", v):
            raise ValueError("El nombre solo puede contener letras y espacios")
        return v.strip()
    
    @validator('usuario')
    def validate_usuario_format(cls, v):
        if not validate_username(v):
            raise ValueError("Usuario debe tener 3-30 caracteres alfanuméricos, puntos, guiones o guiones bajos")
        return v.lower().strip()
    
    @validator('clave')
    def validate_password(cls, v):
        is_valid, message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v
    
    @validator('telefono')
    def validate_telefono_format(cls, v):
        if v and not re.match(r"^\+?[\d\s\-\(\)]{10,15}$", v):
            raise ValueError("Formato de teléfono inválido")
        return v.strip() if v else None
    
    @validator('acepta_terminos')
    def validate_terms(cls, v):
        if not v:
            raise ValueError("Debe aceptar los términos y condiciones")
        return v

class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=8, max_length=128, description="Nueva contraseña")
    confirm_password: str = Field(..., description="Confirmación de nueva contraseña")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        is_valid, message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Las contraseñas no coinciden')
        return v

class SecurePasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico")
    captcha_response: Optional[str] = Field(None, description="Respuesta del captcha")

# Diccionario para tracking de intentos de reset
reset_attempts: dict = {}

def get_client_info(request: Request) -> dict:
    """Obtiene información del cliente para logging"""
    return {
        "ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("User-Agent", "unknown"),
        "referer": request.headers.get("Referer", "unknown")
    }

def sanitize_for_log(data: str) -> str:
    """Sanitiza datos para logging seguro"""
    if not data:
        return "[empty]"
    # Remover caracteres peligrosos y limitar longitud
    sanitized = re.sub(r'[^\w\-@.]', '_', str(data))
    return sanitized[:50] + "..." if len(sanitized) > 50 else sanitized

async def enviar_mensaje_activacion_seguro(
    destino: str, 
    nombre: str, 
    token_activacion: str, 
    tipo: str = 'correo',
    request: Request = None
):
    """Envía mensaje de activación con validaciones de seguridad"""
    try:
        # Validar destinatario
        if tipo == 'correo' and not validar_email(destino):
            raise ValueError("Correo electrónico inválido")
        
        if tipo == 'whatsapp' and not validar_telefono(destino):
            raise ValueError("Número de teléfono inválido")
        
        # Crear enlace de activación seguro
        enlace_activacion = f"{BASE_URL}/activar?token={token_activacion}"
        minutos = int(activation_token_expires.total_seconds() // 60)
        
        mensaje = f"""
        Hola {nombre},
        
        Tu registro ha sido exitoso. Tienes {minutos} minutos para activar tu cuenta.
        
        Haz clic en el siguiente enlace para activar:
        {enlace_activacion}
        
        Si no solicitaste este registro, ignora este mensaje.
        
        Saludos,
        Equipo de Seguridad
        """
        
        if tipo == 'correo':
            await enviar_correo(
                destino, 
                "Activación de cuenta - Acción requerida", 
                mensaje
            )
        elif tipo == 'whatsapp':
            await enviar_mensaje_whatsapp(destino, mensaje)
        
        # Log del envío exitoso
        client_info = get_client_info(request) if request else {}
        log_security_event(
            "ACTIVATION_EMAIL_SENT",
            {
                "destinatario": sanitize_for_log(destino),
                "tipo": tipo,
                **client_info
            },
            "INFO"
        )
        
    except Exception as e:
        logger.error(f"Error enviando mensaje de activación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error enviando mensaje de activación"
        )

@router.get("/users/me")
async def get_my_profile(user: UserDB = Depends(current_user)):
    """Obtiene perfil del usuario actual"""
    try:
        # No incluir información sensible en la respuesta
        profile_data = {
            "codigo": user.codigo,
            "usuario": user.usuario,
            "nombre": user.nombre,
            "mail": user.mail,
            "activo": user.activo,
            "fecha_ultimo_acceso": datetime.now().isoformat()
        }
        
        # Incluir roles si están disponibles
        if hasattr(user, "roles") and user.roles:
            profile_data["roles"] = [
                {"nombre": role.nombre, "descripcion": role.descripcion}
                for role in user.roles
            ]
        
        return profile_data
        
    except Exception as e:
        logger.error(f"Error obteniendo perfil: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obteniendo información del perfil"
        )

@router.get("/usuarios/current")
async def get_current_user_info(user: UserDB = Depends(current_user)):
    """Obtiene información del usuario para el navbar"""
    try:
        user_data = {
            "id": user.codigo,
            "nombre": user.nombre,
            "email": user.mail,
            "usuario": user.usuario,
            "autenticado": True
        }
        
        if hasattr(user, "roles") and user.roles:
            user_data["roles"] = [
                {"id": getattr(role, "id", None), "nombre": getattr(role, "nombre", None)}
                for role in user.roles
            ]
        
        return user_data
        
    except Exception as e:
        logger.error(f"Error obteniendo usuario actual: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obteniendo información del usuario"
        )

@router.get("/activar")
async def activar_cuenta(
    token: str, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Activa cuenta de usuario con validaciones de seguridad"""
    client_info = get_client_info(request)
    
    try:
        # Validar token
        if not token or len(token) > 500:  # Evitar tokens excesivamente largos
            log_security_event(
                "ACTIVATION_FAILED",
                {"reason": "invalid_token_format", **client_info},
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de activación inválido"
            )
        
        # Decodificar token
        usuario = decodifica_token(token)
        if not usuario:
            log_security_event(
                "ACTIVATION_FAILED",
                {"reason": "token_decode_failed", **client_info},
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de activación expirado o inválido"
            )
        
        # Activar usuario
        result = update_usuario_activate(db, usuario)
        
        if not result:
            log_security_event(
                "ACTIVATION_FAILED",
                {"reason": "user_not_found", "usuario": sanitize_for_log(usuario), **client_info},
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        log_security_event(
            "ACCOUNT_ACTIVATED",
            {"usuario": sanitize_for_log(usuario), **client_info},
            "INFO"
        )
        
        return JSONResponse(
            content={"message": f"Cuenta de {usuario} activada exitosamente"},
            status_code=status.HTTP_200_OK
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activando cuenta: {str(e)}")
        log_security_event(
            "ACTIVATION_ERROR",
            {"error": str(e), **client_info},
            "ERROR"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno durante la activación"
        )

@router.post("/user/registro")
async def registrar_usuario(
    usuario_data: UserRegistration, 
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Registra nuevo usuario con validaciones de seguridad"""
    client_info = get_client_info(request)
    
    try:
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
        
        # Verificar email duplicado
        # Aquí deberías implementar una función para verificar email duplicado
        
        # Encriptar contraseña
        clave_encriptada = encriptar_clave(usuario_data.clave)
        
        # Crear usuario
        result = create_usuario(
            db=db,
            nombre=usuario_data.nombre,
            usuario=usuario_data.usuario,
            clave=clave_encriptada,
            mail=usuario_data.mail
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
        
        # Enviar email de activación (en background)
        if validar_email(usuario_data.mail):
            background_tasks.add_task(
                enviar_mensaje_activacion_seguro,
                usuario_data.mail,
                usuario_data.nombre,
                token_activacion,
                'correo',
                request
            )
        
        # Enviar WhatsApp si se proporcionó teléfono
        if usuario_data.telefono and validar_telefono(usuario_data.telefono):
            background_tasks.add_task(
                enviar_mensaje_activacion_seguro,
                usuario_data.telefono,
                usuario_data.nombre,
                token_activacion,
                'whatsapp',
                request
            )
        
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
                "message": "Usuario registrado exitosamente",
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
            detail="Error interno durante el registro"
        )

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_info: dict

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Autentica usuario con seguridad mejorada"""
    client_info = get_client_info(request) if request else {}
    
    try:
        # Validar entrada
        if not form_data.username or not form_data.password:
            log_security_event(
                "LOGIN_FAILED",
                {"reason": "empty_credentials", **client_info},
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Credenciales requeridas"
            )
        
        # Autenticar usuario
        user = authenticate_user(db, form_data.username, form_data.password, request)
        
        if not user:
            # El logging ya se hace en authenticate_user
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
          # Crear token de acceso
        access_token = crear_access_token(
            data={"sub": user["username"]},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_DURATION),
            scopes=["read", "write"]  # Agregar scopes según necesidad
        )
        
        # Preparar respuesta
        response_data = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_DURATION * 60,  # En segundos
            user_info={
                "username": user["username"],
                "nombre": user["nombre"],
                "roles": user.get("roles", [])
            }
        )
        
        # Crear respuesta con cookie segura
        response = JSONResponse(content=response_data.dict())
        
        # Configurar cookie segura
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=ACCESS_TOKEN_DURATION * 60,
            httponly=True,  # Previene acceso desde JavaScript
            secure=True,    # Solo HTTPS en producción
            samesite="lax"  # Protección CSRF
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        log_security_event(
            "LOGIN_ERROR",
            {"error": str(e), **client_info},
            "ERROR"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno durante el login"
        )

@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    user: UserDB = Depends(current_user)
):
    """Cierra sesión de forma segura"""
    client_info = get_client_info(request)
    
    try:
        # Obtener token actual
        token = request.cookies.get('access_token')
        if not token:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # Revocar token si existe
        if token:
            payload = decodifica_token(token)
            if payload and payload.get("jti"):
                expires_at = datetime.fromtimestamp(payload.get("exp", 0))
                revoke_token(payload["jti"], expires_at)
        
        # Limpiar cookie
        response.delete_cookie(
            key="access_token",
            httponly=True,
            secure=True,
            samesite="lax"
        )
        
        log_security_event(
            "USER_LOGOUT",
            {"usuario": sanitize_for_log(user.usuario), **client_info},
            "INFO"
        )
        
        return {"message": "Sesión cerrada exitosamente"}
        
    except Exception as e:
        logger.error(f"Error en logout: {str(e)}")
        return {"message": "Logout procesado"}

@router.post("/password-reset-request")
async def password_reset_request(
    request_data: SecurePasswordResetRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Solicita reset de contraseña con protecciones de seguridad"""
    client_info = get_client_info(request)
    client_ip = client_info.get("ip", "unknown")
    
    try:
        # Rate limiting para reset requests
        current_time = datetime.now()
        if client_ip in reset_attempts:
            attempts = reset_attempts[client_ip]
            # Limpiar intentos antiguos
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
        
        # Buscar usuario
        user = db.query(UsuariosModel).filter(
            UsuariosModel.mail == request_data.email
        ).first()
        
        if user:
            # Crear token de reset
            reset_token = crear_access_token(
                data={
                    "sub": user.usuario,
                    "type": "password_reset",
                    "email": request_data.email
                },
                expires_delta=password_reset_expires
            )
            
            # Enviar email en background
            reset_link = f"{BASE_URL}/reset-password?token={reset_token}"
            message = f"""
            Solicitud de restablecimiento de contraseña.
            
            Si solicitaste restablecer tu contraseña, haz clic en el siguiente enlace:
            {reset_link}
            
            Este enlace expira en 1 hora.
            
            Si no solicitaste esto, ignora este mensaje.
            """
            
            background_tasks.add_task(
                enviar_correo,
                request_data.email,
                "Restablecimiento de contraseña",
                message
            )
        
        # Registrar intento (independientemente si el usuario existe)
        if client_ip not in reset_attempts:
            reset_attempts[client_ip] = []
        reset_attempts[client_ip].append(current_time)
        
        log_security_event(
            "PASSWORD_RESET_REQUESTED",
            {"email": sanitize_for_log(request_data.email), **client_info},
            "INFO"
        )
        
        # Respuesta genérica por seguridad
        return {
            "message": "Si el correo está registrado, recibirás instrucciones para restablecer tu contraseña"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en password reset request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno procesando solicitud"
        )

@router.get("/loginpage", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/registerpage", response_class=HTMLResponse)
async def register_page(request: Request):
    """Página de registro"""
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/check-auth")
async def check_auth(request: Request):
    """Verifica estado de autenticación"""
    try:
        token = request.cookies.get('access_token')
        if not token:
            return {"authenticated": False}
        
        payload = decodifica_token(token)
        if payload and payload.get("sub"):
            return {"authenticated": True, "username": payload["sub"]}
        
        return {"authenticated": False}
        
    except Exception:
        return {"authenticated": False}

@router.get("/protected")
async def protected_route(user: UserDB = Depends(current_user)):
    """Ruta protegida para probar JWT - Para pruebas de seguridad"""
    try:
        return {
            "message": "Access granted",
            "user": user.usuario,
            "id": user.codigo,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error en ruta protegida: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno en ruta protegida"
        )
