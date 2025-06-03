"""
Servidor simple para probar las funciones de seguridad
Este servidor incluye solo las rutas esenciales para las pruebas de seguridad
"""

from fastapi import FastAPI, HTTPException, Form, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
import uvicorn
from datetime import datetime, timedelta
import jose.jwt as jwt
import hashlib
import time
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="Security Test Server")

# Configuración JWT
SECRET_KEY = os.getenv("SECRET", "default-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_DURATION", "30").split('#')[0].strip())

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Rate limiting simple en memoria
rate_limit_store = {}
RATE_LIMIT_MAX_ATTEMPTS = int(os.getenv("RATE_LIMIT_MAX_ATTEMPTS", "5").split('#')[0].strip())
RATE_LIMIT_TIME_WINDOW = int(os.getenv("RATE_LIMIT_TIME_WINDOW", "60").split('#')[0].strip())

class UserCreate(BaseModel):
    nombre: str
    usuario: str
    clave: str
    mail: str

class Token(BaseModel):
    access_token: str
    token_type: str

def check_rate_limit(client_ip: str) -> bool:
    """Verificar rate limiting"""
    current_time = time.time()
    
    # Limpiar entradas antiguas
    cutoff_time = current_time - RATE_LIMIT_TIME_WINDOW
    rate_limit_store[client_ip] = [
        timestamp for timestamp in rate_limit_store.get(client_ip, [])
        if timestamp > cutoff_time
    ]
    
    # Verificar si excede el límite
    attempts = len(rate_limit_store.get(client_ip, []))
    if attempts >= RATE_LIMIT_MAX_ATTEMPTS:
        return False
    
    # Agregar nuevo intento
    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = []
    rate_limit_store[client_ip].append(current_time)
    
    return True

def validate_password(password: str) -> bool:
    """Validar fortaleza de contraseña"""
    min_length = int(os.getenv("PASSWORD_MIN_LENGTH", "8").split('#')[0].strip())
    require_uppercase = os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").split('#')[0].strip().lower() == "true"
    require_lowercase = os.getenv("PASSWORD_REQUIRE_LOWERCASE", "true").split('#')[0].strip().lower() == "true"
    require_numbers = os.getenv("PASSWORD_REQUIRE_NUMBERS", "true").split('#')[0].strip().lower() == "true"
    require_special = os.getenv("PASSWORD_REQUIRE_SPECIAL", "true").split('#')[0].strip().lower() == "true"
    
    if len(password) < min_length:
        return False
    
    if require_uppercase and not any(c.isupper() for c in password):
        return False
    
    if require_lowercase and not any(c.islower() for c in password):
        return False
    
    if require_numbers and not any(c.isdigit() for c in password):
        return False
    
    if require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False
    
    return True

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verificar token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None

@app.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint de login con rate limiting"""
    client_ip = "127.0.0.1"  # En un entorno real, obtener IP real
    
    # Verificar rate limiting
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Please try again later."
        )
    
    # Simular autenticación fallida para pruebas
    if form_data.username == "usuario_falso":
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    # Crear token para usuarios válidos
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/user/registro")
async def register_user(user_data: UserCreate):
    """Endpoint de registro con validación de contraseñas"""
    
    # Validar contraseña
    if not validate_password(user_data.clave):
        raise HTTPException(
            status_code=400,
            detail="Password does not meet security requirements"
        )
    
    # Simular registro exitoso
    return {"message": "User registered successfully", "user_id": 123}

@app.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    """Ruta protegida para probar JWT"""
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )
    
    return {"message": "Access granted", "user": payload.get("sub")}

@app.get("/users/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Ruta para obtener usuario actual - para pruebas JWT"""
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )
    
    return {"username": payload.get("sub"), "id": 1}

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {"message": "Security Test Server is running"}

@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
