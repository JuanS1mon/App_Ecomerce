# backend/routers/usuarios.py

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from datetime import timedelta
import logging

# Instancias de FastAPI y dependencias
router = APIRouter(
    include_in_schema=False,  # Oculta todas las rutas de este router en la documentación,
    tags=["usuario"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

from Services.security.security import (
    authenticate_user,
    current_user,
    encriptar_clave,
    verificar_clave,
    crear_access_token,
    access_token_expires,
    decodifica_token
)
from Services.mail import enviar_correo, validar_email
from Services.whassap import enviar_mensaje_whatsapp, validar_telefono

from db.crud.Maestro.Usuarios import (
    get_usuario,
    create_usuario,
    update_usuario_activate
)
from db.database import get_db
from db.schemas.Maestro.Usuarios import (
    UserDB,
    PasswordReset,
    PasswordResetRequest
)
from db.models.usuarios import usuarios as UsuariosModel

from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()
BASE_URL = os.getenv("BASE_URL")



activation_token_expires = timedelta(minutes=10)

# Configurar Jinja2Templates para buscar en el directorio "static"
templates = Jinja2Templates(directory="static")

class UserRegistration(BaseModel):
    nombre: str
    usuario: str
    clave: str
    mail: str
    telefono: str = None  # Puede ser opcional

def enviar_mensaje_activacion(destino, nombre, token_activacion, activation_token_expires, tipo, asunto=None):
    enlace_activacion = f"{BASE_URL}/activar?token={token_activacion}"
    minutos = int(activation_token_expires.total_seconds() // 60)
    mensaje = f"Hola {nombre}, tu registro ha sido exitoso. Tienes {minutos} minutos para activar tu cuenta, haz clic en el siguiente enlace: {enlace_activacion}"
    
    if tipo == 'correo':
        if asunto is None:
            raise ValueError("El asunto es requerido para enviar un correo electrónico.")
        enviar_correo(destino, asunto, mensaje)
    elif tipo == 'whatsapp':
        enviar_mensaje_whatsapp(destino, mensaje)
    else:
        raise ValueError("Tipo de mensaje no soportado. Use 'correo' o 'whatsapp'.")

@router.get("/users/me")
async def me(user: UserDB = Depends(current_user)):
    return user

@router.get("/activar")
async def activar_cuenta(token: str, db: Session = Depends(get_db)):
    usuario = decodifica_token(token)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido")
    
    update_usuario_activate(db, usuario)
    return {"message": f"Cuenta de {usuario} activada exitosamente"}

@router.post("/user/registro")
async def registrar_usuario(usuario: UserRegistration, db: Session = Depends(get_db)):
    if not all([usuario.nombre, usuario.usuario, usuario.clave, usuario.mail]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Todos los campos son requeridos")
    
    if get_usuario(db, usuario=usuario.usuario):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario ya registrado")
    
    clave_encriptada = encriptar_clave(usuario.clave)
    result = create_usuario(db=db, nombre=usuario.nombre, usuario=usuario.usuario, clave=clave_encriptada, mail=usuario.mail)

    if validar_email(usuario.mail):
        token_activacion = crear_access_token(data={"sub": usuario.usuario}, expires_delta=activation_token_expires)
        enviar_mensaje_activacion(usuario.mail, usuario.nombre, token_activacion, activation_token_expires, 'correo', asunto='Activación de cuenta')
    
    if usuario.telefono:
        enviar_mensaje_activacion(usuario.telefono, usuario.nombre, token_activacion, activation_token_expires, 'whatsapp')
    
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
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = crear_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
    response.set_cookie(
        key="access_token",
        value=f"{access_token}",
        httponly=True,
        secure=False,  # Cambiar a False en desarrollo
        samesite="Lax"
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/ruta-protegida")
async def protected_route(user: UserDB = Depends(current_user)):
    return {"message": "Tienes acceso a esta ruta", "user": user.usuario}

@router.get("/users/me/{codigo}")
async def gets_usuario(codigo: int, db: Session = Depends(get_db), user: UserDB = Depends(current_user)):
    db_usuario = get_usuario(db, codigo=codigo)
    if not db_usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario no encontrado")
    return db_usuario

@router.post("/password-reset-request")
async def password_reset_request(request: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(UsuariosModel).filter(UsuariosModel.mail == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    token = crear_access_token(data={"sub": user.usuario}, expires_delta=timedelta(hours=1))
    reset_link = f"{BASE_URL}/reset-password?token={token}"
    enviar_correo(request.email, "Restablecimiento de contraseña", f"Para restablecer tu contraseña, haz clic en el siguiente enlace: {reset_link}")
    
    return {"message": "Se ha enviado un enlace de restablecimiento de contraseña a tu correo electrónico"}

@router.post("/reset-password")
async def reset_password(reset: PasswordReset, db: Session = Depends(get_db)):
    try:
        payload = decodifica_token(reset.token)
        usuario = payload.get("sub")
        if usuario is None:
            raise HTTPException(status_code=400, detail="Token inválido o expirado")
    except:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
    
    user = db.query(UsuariosModel).filter(UsuariosModel.usuario == usuario).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user.clave = encriptar_clave(reset.new_password)
    db.commit()
    
    return {"message": "Contraseña restablecida con éxito"}

@router.get("/loginpage", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/registerpage", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/index", status_code=303)
    response.delete_cookie("access_token")
    return response
