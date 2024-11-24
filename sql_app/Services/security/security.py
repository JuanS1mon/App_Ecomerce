from fastapi import HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from db.database import get_db
from db.crud.Maestro.Usuarios import get_usuario, user_pass, get_user_from_db
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from typing import Optional
from db.schemas.Maestro.Usuarios import UserDB

# Carga las variables de entorno del archivo .env
load_dotenv()

# Variables de configuración
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_DURATION = int(os.getenv("ACCESS_TOKEN_DURATION", 30))  # Valor por defecto de 30 minutos
SECRET = os.getenv("SECRET")
TOKEN_EXPIRE_MINUTES = 30

class TokenData(BaseModel):
    username: Optional[str] = None

# Configuración de passlib
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2 = OAuth2PasswordBearer(tokenUrl="/login")

# Calcular el tiempo de expiración del token
access_token_expires = timedelta(minutes=ACCESS_TOKEN_DURATION)

def encriptar_clave(clave):
    return pwd_context.hash(clave)

def verificar_clave(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

def decodifica_token(token: str):
    print(f"Token recibido: {token}")
    try:
        # Eliminar caracteres adicionales si están presentes
        token = token.strip().rstrip('/')
        print(f"Token procesado: {token}")
        
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        print(f"Payload decodificado: {payload}")
        
        usuario = payload.get("sub")
        return usuario
    except jwt.ExpiredSignatureError:
        print("Token expirado")
        return None
    except jwt.InvalidTokenError:
        print("Token inválido")
        return None


def crear_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)


def authenticate_user(db: Session, username: str, password: str):
    user_info = user_pass(db, username, password)
    if not user_info:
        return None
    hashed_password = user_info["password"]
    if not verificar_clave(password, hashed_password):
        return None
    return {"username": username, "password": hashed_password}

def auth_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = get_user_from_db(db, username)
        if user is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user

def current_user(user: UserDB = Depends(auth_user)):
    if not user.activo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario deshabilitado")
    return user

def generar_token_activacion(usuario_id):
    payload = {
        'usuario_id': usuario_id,
        'exp': datetime.utcnow() + timedelta(days=1)  # Expira en 1 día
    }
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    return token

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    # Obtener el token de la cookie
    token = request.cookies.get('access_token')
    print(f"Token recibido: {token}")
    
    if not token:
        # Intentar obtener el token del encabezado Authorization
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            print(f"Token obtenido del encabezado Authorization: {token}")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Decodificar el token
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Obtener usuario de la base de datos
        user = get_user_from_db(db, username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar si el usuario está activo
        if not user.activo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario deshabilitado",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return user
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )