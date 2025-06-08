"""
Router de usuarios mejorado con seguridad avanzada
Incluye validaciones robustas, logging seguro y protección contra ataques
"""

"""

Router de usuarios mejorado con seguridad avanzada
Incluye validaciones robustas, logging seguro y protección contra ataques
"""

"""

Router de usuarios mejorado con seguridad avanzada
Incluye validaciones robustas, logging seguro y protección contra ataques
"""

"""

Router de usuarios mejorado con seguridad avanzada
Incluye validaciones robustas, logging seguro y protección contra ataques
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status, BackgroundTasks, Request
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse, FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
import httpx
from pydantic import BaseModel, EmailStr, field_validator, Field
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from datetime import timedelta, datetime
import logging
import secrets
import re
import jwt
from jose import JWTError
from typing import Optional

# Importar versiones mejoradas de seguridad
from ..Services.security.security import (ACCESS_TOKEN_DURATION, authenticate_user, current_user, encriptar_clave, verificar_clave, crear_access_token,decodifica_token,validate_username,validate_password_strength,log_security_event,revoke_token,generar_token_activacion, SECRET, ALGORITHM, get_current_user)
from ..Services.security.get_optional_user import get_optional_user
from ..Services.mail.mail import enviar_email_simple, validar_email
from ..Services.comunicacion.whassap import enviar_mensaje_whatsapp, validar_telefono
from ..db.crud.config.Usuarios import (
    get_usuario, 
    create_usuario, update_usuario_activate
)
from ..db.database import get_db
from ..db.schemas.config.Usuarios import (
    UserDB, 
    PasswordReset, 
    PasswordResetRequest
)
from ..db.models.config.usuarios import usuarios as UsuariosModel

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
templates = Jinja2Templates(directory="sql_app/static")

# Modelos mejorados con validación
class UserRegistration(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre completo")
    usuario: str = Field(..., min_length=3, max_length=30, description="Nombre de usuario")
    clave: str = Field(..., min_length=3, max_length=128, description="Contraseña")
    mail: EmailStr = Field(..., description="Correo electrónico")
    telefono: Optional[str] = Field(None, min_length=10, max_length=15, description="Teléfono")
    acepta_terminos: bool = Field(..., description="Aceptación de términos y condiciones")
    
    @field_validator('nombre')
    @classmethod
    def validate_nombre(cls, v):
        # Limpiar espacios
        v = v.strip()
        
        # Verificar longitud mínima
        if len(v) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")
        
        # Permitir letras, espacios, acentos y números (más permisivo para casos como "juan13")
        # También permite guiones, apostrofes y puntos para nombres compuestos
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s\-\.\']+$", v):
            raise ValueError("El nombre contiene caracteres no válidos. Solo se permiten letras, números, espacios y algunos signos básicos")
        
        return v
        
    @field_validator('usuario')
    @classmethod
    def validate_usuario_format(cls, v):
        if not validate_username(v):
            raise ValueError("Usuario debe tener 3-30 caracteres alfanuméricos, puntos, guiones o guiones bajos")
        return v.lower().strip()
        
    @field_validator('clave')
    @classmethod
    def validate_password(cls, v):
        # Se ha simplificado la validación para permitir contraseñas más simples
        if len(v) < 3:
            raise ValueError("La contraseña debe tener al menos 3 caracteres")
        return v
        
    @field_validator('telefono')
    @classmethod
    def validate_telefono_format(cls, v):
        if v and not re.match(r"^\+?[\d\s\-\(\)]{10,15}$", v):
            raise ValueError("Formato de teléfono inválido")
        return v.strip() if v else None
    
    @field_validator('acepta_terminos')
    @classmethod
    def validate_terms(cls, v):
        if not v:
            raise ValueError("Debe aceptar los términos y condiciones")
        return bool(v)

class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=3, max_length=128, description="Nueva contraseña")
    confirm_password: str = Field(..., description="Confirmación de nueva contraseña")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 3:
            raise ValueError("La contraseña debe tener al menos 3 caracteres")
        return v
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Las contraseñas no coinciden')
        return v

class SecurePasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico")
    captcha_response: Optional[str] = Field(None, description="Respuesta del captcha")

class ConfirmPasswordReset(BaseModel):
    token: str = Field(..., description="Token de reset")
    new_password: str = Field(..., min_length=3, max_length=128, description="Nueva contraseña")
    confirm_password: str = Field(..., description="Confirmación de nueva contraseña")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 3:
            raise ValueError("La contraseña debe tener al menos 3 caracteres")
        return v
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Las contraseñas no coinciden')
        return v

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
        Equipo de Seguridad        """
        
        if tipo == 'correo':
            try:
                enviar_email_simple(
                    destino, 
                    "Activación de cuenta - Acción requerida", 
                    mensaje
                )
            except Exception as e:
                logger.error(f"Error enviando email de activación: {str(e)}")
                # No lanzar excepción aquí, solo loggear
                return
        elif tipo == 'whatsapp':
            try:
                # Verificar si la función es async o no
                whatsapp_result = enviar_mensaje_whatsapp(destino, mensaje)
                if whatsapp_result is not None and hasattr(whatsapp_result, '__await__'):
                    await whatsapp_result
            except Exception as e:
                logger.error(f"Error enviando WhatsApp: {str(e)}")
                # No lanzar excepción aquí, solo loggear
                return
        
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
        # No lanzar HTTPException en background task
        return

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
async def get_current_user_info(request: Request, user: UserDB = Depends(get_current_user)):
    """Obtiene información del usuario para el navbar"""
    logger.info(f"🔍 DEBUG: Iniciando get_current_user_info")
    logger.info(f"🔍 DEBUG: Usuario recibido: {user}")
    logger.info(f"🔍 DEBUG: Tipo de usuario: {type(user)}")
    
    # Esto NO debería ejecutarse nunca si get_current_user funciona correctamente
    return {
        "mensaje": "ENDPOINT CORREGIDO EJECUTANDOSE",
        "debug": True,
        "user_type": str(type(user)),
        "user_data": str(user) if user else "None"
    }

@router.get("/activar", response_class=HTMLResponse)
async def activar_cuenta_page(
    request: Request,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Muestra la página de activación de cuenta y procesa la activación si hay token"""
    client_info = get_client_info(request)
    
    # Si hay un token en la URL, procesar la activación directamente
    if token:
        try:
            # Validar token
            if not token or len(token) > 500:
                log_security_event(
                    "ACTIVATION_FAILED",
                    {"reason": "invalid_token_format", **client_info},
                    "WARNING"
                )
                error_html = """
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <title>Error de Activación</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f8f9fa; }
                        .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                        .error { color: #dc3545; font-size: 24px; margin-bottom: 20px; }
                        .btn { background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px; display: inline-block; }
                        .btn:hover { background: #0056b3; }
                        .btn-secondary { background: #6c757d; }
                        .btn-secondary:hover { background: #545b62; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1 class="error">❌ Error de Activación</h1>
                        <p>Token de activación inválido o malformado</p>
                        <div>
                            <a href="/registerpage" class="btn">Registrarse Nuevamente</a>
                            <a href="/loginpage" class="btn btn-secondary">Iniciar Sesión</a>
                        </div>
                    </div>
                </body>
                </html>
                """
                return HTMLResponse(content=error_html, status_code=400)
            
            # Decodificar token
            usuario = decodifica_token(token)
            if not usuario:
                log_security_event(
                    "ACTIVATION_FAILED",
                    {"reason": "token_decode_failed", **client_info},
                    "WARNING"
                )
                error_html = """
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <title>Token Expirado</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f8f9fa; }
                        .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                        .error { color: #dc3545; font-size: 24px; margin-bottom: 20px; }
                        .btn { background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px; display: inline-block; }
                        .btn:hover { background: #0056b3; }
                        .btn-secondary { background: #6c757d; }
                        .btn-secondary:hover { background: #545b62; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1 class="error">⏰ Token Expirado</h1>
                        <p>El token de activación ha expirado o es inválido</p>
                        <p>Por favor, regístrate nuevamente para obtener un nuevo token.</p>
                        <div>
                            <a href="/registerpage" class="btn">Registrarse Nuevamente</a>
                            <a href="/loginpage" class="btn btn-secondary">Iniciar Sesión</a>
                        </div>
                    </div>
                </body>
                </html>
                """
                return HTMLResponse(content=error_html, status_code=400)
            
            # Activar usuario
            result = update_usuario_activate(db, usuario)
            
            if not result:
                log_security_event(
                    "ACTIVATION_FAILED",
                    {"reason": "user_not_found", "usuario": sanitize_for_log(usuario), **client_info},
                    "WARNING"
                )
                error_html = """
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <title>Usuario No Encontrado</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f8f9fa; }
                        .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                        .error { color: #dc3545; font-size: 24px; margin-bottom: 20px; }
                        .btn { background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px; display: inline-block; }
                        .btn:hover { background: #0056b3; }
                        .btn-secondary { background: #6c757d; }
                        .btn-secondary:hover { background: #545b62; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1 class="error">👤 Usuario No Encontrado</h1>
                        <p>No se pudo encontrar el usuario para activar</p>
                        <p>Es posible que la cuenta ya haya sido activada o eliminada.</p>
                        <div>
                            <a href="/registerpage" class="btn">Registrarse Nuevamente</a>
                            <a href="/loginpage" class="btn btn-secondary">Iniciar Sesión</a>
                        </div>
                    </div>
                </body>
                </html>
                """
                return HTMLResponse(content=error_html, status_code=404)
            
            log_security_event(
                "ACCOUNT_ACTIVATED",
                {"usuario": sanitize_for_log(usuario), **client_info},
                "INFO"
            )
            
            # Mostrar página de éxito
            success_html = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>Cuenta Activada</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f8f9fa; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                    .success {{ color: #28a745; font-size: 24px; margin-bottom: 20px; }}
                    .btn {{ background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px; display: inline-block; }}
                    .btn:hover {{ background: #1e7e34; }}
                    .btn-secondary {{ background: #6c757d; }}
                    .btn-secondary:hover {{ background: #545b62; }}
                    .highlight {{ background-color: #fff3cd; padding: 10px; border-radius: 5px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 class="success">✅ ¡Cuenta Activada Exitosamente!</h1>
                    <div class="highlight">
                        <p>La cuenta de <strong>{usuario}</strong> ha sido activada correctamente.</p>
                    </div>
                    <p>Ya puedes iniciar sesión con tus credenciales.</p>
                    <div>
                        <a href="/loginpage" class="btn">Iniciar Sesión</a>
                        <a href="/" class="btn btn-secondary">Volver al Inicio</a>
                    </div>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=success_html, status_code=200)
            
        except Exception as e:
            logger.error(f"Error activando cuenta: {str(e)}")
            log_security_event(
                "ACTIVATION_ERROR",
                {"error": str(e), **client_info},
                "ERROR"
            )
            error_html = """
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>Error Interno</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f8f9fa; }
                    .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                    .error { color: #dc3545; font-size: 24px; margin-bottom: 20px; }
                    .btn { background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px; display: inline-block; }
                    .btn:hover { background: #0056b3; }
                    .btn-secondary { background: #6c757d; }
                    .btn-secondary:hover { background: #545b62; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 class="error">⚠️ Error Interno</h1>
                    <p>Ocurrió un error durante la activación</p>
                    <p>Por favor, intenta nuevamente o contacta al soporte.</p>
                    <div>
                        <a href="/registerpage" class="btn">Registrarse Nuevamente</a>
                        <a href="/loginpage" class="btn btn-secondary">Iniciar Sesión</a>
                    </div>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=error_html, status_code=500)
    
    # Si no hay token, mostrar página de activación manual
    manual_activation_html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Activar Cuenta</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; background-color: #f8f9fa; }
            .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input[type="text"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; width: 100%; }
            button:hover { background: #0056b3; }
            button:disabled { background: #6c757d; cursor: not-allowed; }
            .link { text-align: center; margin-top: 15px; }
            .link a { color: #007bff; text-decoration: none; }
            .link a:hover { text-decoration: underline; }
            .title { color: #007bff; text-align: center; margin-bottom: 30px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="title">📧 Activar Cuenta</h1>
            <p>Ingresa el token de activación que recibiste por correo:</p>
            
            <form id="activationForm">
                <div class="form-group">
                    <label for="token">Token de Activación:</label>
                    <input type="text" id="token" name="token" required placeholder="Pega aquí tu token de activación...">
                </div>
                <button type="submit" id="submitBtn">Activar Cuenta</button>
            </form>
            
            <div class="link">
                <a href="/loginpage">¿Ya tienes cuenta activa? Iniciar sesión</a>
            </div>
        </div>

        <script>
            document.getElementById('activationForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const token = document.getElementById('token').value.trim();
                const submitBtn = document.getElementById('submitBtn');
                
                if (!token) {
                    alert('Por favor ingresa el token de activación');
                    return;
                }
                
                submitBtn.disabled = true;
                submitBtn.textContent = 'Activando...';
                
                try {
                    const response = await fetch('/api/activar', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ token: token })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        alert('¡Cuenta activada exitosamente!');
                        window.location.href = '/loginpage';
                    } else {
                        alert(data.detail || 'Error activando la cuenta');
                    }
                } catch (error) {
                    alert('Error de conexión. Intenta nuevamente.');
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Activar Cuenta';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=manual_activation_html, status_code=200)

@router.post("/api/activar")
async def activar_cuenta_api(
    request: Request,
    db: Session = Depends(get_db)
):
    """API para activar cuenta de usuario con validaciones de seguridad"""
    client_info = get_client_info(request)
    
    try:
        # Obtener el token del body del request
        body = await request.json()
        token = body.get("token")
        
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
            content={
                "message": f"Cuenta de {usuario} activada exitosamente",
                "usuario": usuario,
                "success": True
            },
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
    
    # Log de diagnóstico para ver los datos recibidos
    logger.info(f"Datos de registro recibidos: nombre={usuario_data.nombre}, usuario={usuario_data.usuario}, mail={usuario_data.mail}, acepta_terminos={usuario_data.acepta_terminos}")
    
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
        
        # Comentar temporalmente el WhatsApp hasta que se configure correctamente
        # if usuario_data.telefono and validar_telefono(usuario_data.telefono):
        #     background_tasks.add_task(
        #         enviar_mensaje_activacion_seguro,
        #         usuario_data.telefono,
        #         usuario_data.nombre,
        #         token_activacion,
        #         'whatsapp',
        #         request
        #     )
        
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
        
        if not user:            # El logging ya se hace en authenticate_user
            log_security_event(
                "LOGIN_FAILED",
                {"reason": "invalid_credentials", "username": form_data.username, **client_info},
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )          # Crear token de acceso con información completa
        data = {
            "sub": user["username"],
            "scopes": ["read", "write"],  # Incluimos los scopes en el payload
            "nombre": user["nombre"],
            "roles": [role["nombre"] for role in user.get("roles", [])] if user.get("roles") else ["user"]
        }
        access_token = crear_access_token(
            data=data,
            expires_delta=timedelta(minutes=ACCESS_TOKEN_DURATION)
        )
        
        log_security_event(
            "LOGIN_SUCCESS",
            {"username": user["username"], **client_info},
            "INFO"
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
        
        # Configurar cookie segura - usamos SameSite=None para facilitar el desarrollo
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=ACCESS_TOKEN_DURATION * 60,
            httponly=True,  # Previene acceso desde JavaScript (mantener para producción)
            secure=False,   # Cambiado a False para entorno de desarrollo (en producción debería ser True)
            samesite="lax"  # Cambiado a lax para permitir redirecciones entre sitios
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

@router.post("/logout-test")
async def logout_test():
    """Endpoint de prueba para verificar que POST funciona"""
    return {"message": "Test logout endpoint funcionando", "status": "ok"}

@router.post("/logout-simple")
async def logout_simple():
    """Logout simplificado para diagnóstico"""
    return {"message": "Logout simple exitoso", "status": "ok"}

@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    user: Optional[UserDB] = Depends(get_optional_user)
):
    """Cierra sesión de forma segura"""
    try:
        # Obtener información del cliente para logging
        client_info = {
            "ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown")
        }
        
        # Obtener token actual
        token = request.cookies.get('access_token')
        if not token:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # Revocar token si existe
        if token:
            try:
                payload = decodifica_token(token)
                if payload and payload.get("jti"):
                    expires_at = datetime.fromtimestamp(payload.get("exp", 0))
                    revoke_token(payload["jti"], expires_at)
            except Exception as e:
                logger.warning(f"Error al revocar token en logout: {e}")
        
        # Limpiar cookie siempre
        response.delete_cookie(
            key="access_token",
            httponly=True,
            secure=True,
            samesite="lax"
        )
        
        # Log del evento de logout
        user_info = user.usuario if user else "anonymous"
        log_security_event(
            "USER_LOGOUT",
            {"usuario": user_info, **client_info},
            "INFO"
        )
        
        return {"message": "Sesión cerrada exitosamente", "status": "success"}
        
    except Exception as e:
        logger.error(f"Error en logout: {str(e)}")
        # Limpiar cookie incluso si hay error
        response.delete_cookie(
            key="access_token",
            httponly=True,
            secure=True,
            samesite="lax"
        )
        return {"message": "Sesión cerrada", "status": "processed"}

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
            reset_link = f"{BASE_URL}/confirm-password-reset?token={reset_token}"
            message = f"""
            Solicitud de restablecimiento de contraseña.
            
            Si solicitaste restablecer tu contraseña, haz clic en el siguiente enlace:
            {reset_link}
            
            Este enlace expira en 1 hora.
              Si no solicitaste esto, ignora este mensaje.
            """
            
            background_tasks.add_task(
                enviar_email_simple,
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

@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    """Página de recuperación de contraseña"""
    return templates.TemplateResponse("reset_password.html", {"request": request})

@router.post("/reset-password")
async def reset_password_request(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Procesa la solicitud de reset de contraseña"""
    client_info = get_client_info(request) if request else {}
    
    try:
        # En este caso, form_data.username contiene el email
        email = form_data.username
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email requerido"
            )
        
        # Validar formato de email
        if not validar_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de email inválido"
            )
          # Buscar usuario por email
        from db.models.config.usuarios import usuarios as UsuariosModel
        user = db.query(UsuariosModel).filter(UsuariosModel.mail == email).first()
        
        if not user:
            # Por seguridad, no revelamos si el email existe o no
            log_security_event(
                "PASSWORD_RESET_REQUESTED",
                {"email": email, "found": False, **client_info},
                "INFO"
            )
            return {"message": "Si el email existe en nuestro sistema, recibirás un correo con instrucciones"}
        
        # Generar token de reset con estructura correcta
        reset_token = crear_access_token(
            data={
                "sub": user.usuario,
                "type": "password_reset",
                "email": email
            },
            expires_delta=password_reset_expires
        )
        
        # Crear enlace de reset
        reset_link = f"{BASE_URL}/confirm-password-reset?token={reset_token}"
        
        # Enviar email de reset
        try:
            enviar_email_simple(
                email,
                "Recuperación de contraseña",
                f"""
                Hola {user.nombre},
                
                Recibimos una solicitud para restablecer tu contraseña.
                
                Haz clic en el siguiente enlace para crear una nueva contraseña:
                {reset_link}
                
                Este enlace expirará en 30 minutos.
                
                Si no solicitaste este cambio, ignora este mensaje.
                
                Saludos,
                Equipo de Soporte
                """
            )
            
            log_security_event(
                "PASSWORD_RESET_EMAIL_SENT",
                {"email": email, "user_id": user.codigo, **client_info},
                "INFO"
            )
            
        except Exception as e:
            logger.error(f"Error enviando email de reset: {str(e)}")
            # Continuamos sin revelar el error al usuario
        
        return {"message": "Si el email existe en nuestro sistema, recibirás un correo con instrucciones"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en reset de contraseña: {str(e)}")
        log_security_event(
            "PASSWORD_RESET_ERROR",
            {"error": str(e), **client_info},
            "ERROR"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno procesando solicitud"
        )

@router.get("/confirm-password-reset", response_class=HTMLResponse)
async def confirm_password_reset_page(request: Request):
    """Página para confirmar el reset de contraseña con token"""
    return templates.TemplateResponse("confirm_password_reset.html", {"request": request})

@router.post("/confirm-password-reset")
async def confirm_password_reset(
    reset_data: ConfirmPasswordReset,
    request: Request,
    db: Session = Depends(get_db)
):
    """Confirma el reset de contraseña con token y nueva contraseña"""
    client_info = get_client_info(request)
    
    try:        # Verificar y decodificar el token directamente para reset de contraseña
        try:
            # Decodificar el token JWT directamente
            payload = jwt.decode(reset_data.token, SECRET, algorithms=[ALGORITHM])
            
            username = payload.get("sub")
            token_type = payload.get("type")
            email = payload.get("email")
            
            if not username:
                raise ValueError("Token no contiene username")
                
            # Verificar que es un token de reset de contraseña
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
          # Buscar usuario
        from db.models.config.usuarios import usuarios as UsuariosModel
        user = db.query(UsuariosModel).filter(UsuariosModel.usuario == username).first()
        
        if not user:
            log_security_event(
                "PASSWORD_RESET_USER_NOT_FOUND",
                {"username": sanitize_for_log(username), **client_info},
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido o expirado"
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
                detail="Token inválido o expirado"
            )
        
        # Actualizar contraseña
        user.clave = encriptar_clave(reset_data.new_password)
        db.commit()
        
        log_security_event(
            "PASSWORD_RESET_COMPLETED",
            {"username": sanitize_for_log(username), "user_id": user.codigo, **client_info},
            "INFO"
        )
        
        # Enviar email de confirmación
        try:
            enviar_email_simple(
                user.mail,
                "Contraseña cambiada exitosamente",
                f"""
                Hola {user.nombre},
                
                Tu contraseña ha sido cambiada exitosamente.
                
                Si no fuiste tú quien realizó este cambio, por favor contacta al soporte inmediatamente.
                
                Fecha y hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
                
                Saludos,
                Equipo de Soporte
                """
            )
        except Exception as e:
            logger.error(f"Error enviando email de confirmación: {str(e)}")
            # No fallar si el email no se puede enviar
        
        return {"message": "Contraseña cambiada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en confirmación de reset: {str(e)}")
        log_security_event(
            "PASSWORD_RESET_CONFIRM_ERROR",
            {"error": str(e), **client_info},
            "ERROR"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno procesando solicitud"
        )

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

@router.post("/login-test", response_model=TokenResponse)
async def login_test(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Endpoint temporal para diagnosticar problema de routing"""
    # Usar la misma lógica que el login original
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
            log_security_event(
                "LOGIN_FAILED",
                {"username": form_data.username, "reason": "invalid_credentials", **client_info},
                "WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Crear token de acceso
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_DURATION)
        access_token = crear_access_token(
            data={"sub": user.usuario}, expires_delta=access_token_expires
        )
        
        # Preparar información del usuario para la respuesta
        user_info = {
            "username": user.usuario,
            "nombre": user.nombre,
            "mail": user.mail,
            "activo": user.activo,
            "roles": [{"id": role.id, "nombre": role.nombre} for role in user.roles] if user.roles else []
        }
        
        # Log exitoso
        log_security_event(
            "LOGIN_SUCCESS", 
            {"username": user.usuario, **client_info},
            "INFO"
        )
        
        # Crear respuesta con cookie
        response = JSONResponse(
            content={
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_DURATION * 60,
                "user_info": user_info
            }
        )
        
        # Configurar cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=ACCESS_TOKEN_DURATION * 60,
            httponly=True,
            secure=False,  # True en producción con HTTPS
            samesite="lax"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        log_security_event(
            "LOGIN_ERROR",
            {"username": form_data.username, "error": str(e), **client_info},
            "ERROR"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )
