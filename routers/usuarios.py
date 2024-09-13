from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import os
from dotenv import load_dotenv
from datetime import timedelta

from sqlalchemy.orm import Session

from Services.security.security import (authenticate_user, current_user, encriptar_clave, verificar_clave, crear_access_token, access_token_expires, decodifica_token)
from Services.mail import enviar_correo, validar_email
from Services.whassap import enviar_mensaje_whatsapp, validar_telefono

from db.crud.Maestro.Usuarios import (get_usuario, gets_usuarios, create_usuario, delete_usuario, update_usuario, user_pass, update_usuario_activate)
from db.database import get_db
from db.schemas.Maestro.Usuarios import Usuarios, UserDB, PasswordReset, PasswordResetRequest
from db.models.usuarios import usuarios as UsuariosModel
from pydantic import BaseModel
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()
BASE_URL = os.getenv("BASE_URL")

# Instancias de FastAPI y dependencias
router = APIRouter(
    tags=["usuario"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)
activation_token_expires = timedelta(minutes=10)

# Rutas de la API
@router.get("/users/me")
async def me(user: Usuarios = Depends(current_user)):
    return user

def enviar_mensaje_activacion(destino, nombre, token_activacion, activation_token_expires, tipo, asunto=None):
    enlace_activacion = f"{BASE_URL}/activar?token={token_activacion}"
    minutos = int(activation_token_expires.total_seconds() // 60)
    mensaje = f"Hola {nombre}, tu registro ha sido exitoso. Tienes {minutos} minutos para activar tu cuenta, haz clic en el siguiente enlace:  {enlace_activacion}/"
    
    if tipo == 'correo':
        if asunto is None:
            raise ValueError("El asunto es requerido para enviar un correo electrónico.")
        enviar_correo(destino, asunto, mensaje)
    elif tipo == 'whatsapp':
        enviar_mensaje_whatsapp(destino, mensaje)
    else:
        raise ValueError("Tipo de mensaje no soportado. Use 'correo' o 'whatsapp'.")

@router.get("/activar")
async def activar_cuenta(token: str, db: Session = Depends(get_db)):
    try:
        # Decodificar el token
        usuario = decodifica_token(token)
        if usuario is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido")
        
        # Aquí puedes agregar lógica adicional para activar la cuenta en la base de datos si es necesario
        update_usuario_activate(db, usuario)
        return {"message": f"Cuenta de {usuario} activada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo activar la cuenta, comuníquese con el administrador")
    
# Función registrar_usuario
@router.post("/user/registro")
async def registrar_usuario(Usuario: UserDB, db: Session = Depends(get_db)):
    campos_requeridos = ["nombre", "usuario", "clave", "mail"]
    for campo in campos_requeridos:
        if getattr(Usuario, campo) in (None, "", " "):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El campo {campo} es requerido y no puede estar vacío")
    
    db_Usuario = get_usuario(db, usuario=Usuario.usuario)
    if db_Usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario registrado anteriormente")
    
    clave_encriptada = encriptar_clave(Usuario.clave)
    result = create_usuario(db=db, nombre=Usuario.nombre, usuario=Usuario.usuario, clave=clave_encriptada, mail=Usuario.mail)
    
    # Envío de correo electrónico después del registro exitoso
    mail = validar_email(Usuario.mail)
    if mail is not None:
        token_activacion = crear_access_token(data={"sub": Usuario.usuario}, expires_delta=activation_token_expires)
        enviar_mensaje_activacion(Usuario.mail, Usuario.nombre, token_activacion, activation_token_expires, 'correo', asunto='Activación de cuenta')
    
    # Envío de mensaje de activación por WhatsApp si el teléfono está disponible
    if Usuario.telefono:
        enviar_mensaje_activacion(Usuario.telefono, Usuario.nombre, token_activacion, activation_token_expires, 'whatsapp')
    
    return result

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/login", response_model=Token)
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = crear_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=True,
        samesite="Lax"
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/ruta-protegida")
async def protected_route(user: UserDB = Depends(current_user)):
    return {"message": "Tienes acceso a esta ruta", "user": user.usuario}


@router.get("/users/me/{codigo}")
async def gets_Usuario(codigo: int, db: Session = Depends(get_db), user: Usuarios = Depends(current_user)):
    db_Usuario = get_usuario(db, codigo=codigo, usuario=None)
    if not db_Usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario no encontrado")
    return db_Usuario

@router.post("/password-reset-request")
async def password_reset_request(request: PasswordResetRequest, db: Session = Depends(get_db)):
    email = request.email
    user = db.query(UsuariosModel).filter(UsuariosModel.mail == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    token = crear_access_token(data={"sub": user.usuario}, expires_delta=timedelta(hours=1))
    reset_link = f"{BASE_URL}/reset-password?token={token}"
    enviar_correo(email, "Restablecimiento de contraseña", f"Para restablecer tu contraseña, haz clic en el siguiente enlace: {reset_link}")
    
    return {"message": "Se ha enviado un enlace de restablecimiento de contraseña a tu correo electrónico"}

@router.post("/reset-password")
async def reset_password(reset: PasswordReset, db: Session = Depends(get_db)):
    # Decodificar el token para obtener el usuario
    try:
        payload = decodifica_token(reset.token)
        usuario = payload.get("sub")
        if usuario is None:
            raise HTTPException(status_code=400, detail="Token inválido o expirado")
    except:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
    
    # Buscar el usuario en la base de datos
    user = db.query(UsuariosModel).filter(UsuariosModel.usuario == usuario).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Actualizar la contraseña del usuario
    user.clave = encriptar_clave(reset.new_password)
    db.commit()
    
    return {"message": "Contraseña restablecida con éxito"}

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

# Configurar Jinja2Templates para buscar en el directorio "static"
templates = Jinja2Templates(directory="static")

@router.get("/loginpage", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/registerpage", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})