from fastapi import APIRouter, HTTPException, status, Depends, Response
from fastapi.responses import RedirectResponse


from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt,JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from db.database import  get_db, SessionLocal
from db.schemas.Maestro.Usuarios import UsuarioCreate,Usuario,UsuarioRead,LoginForm
from db.crud.Maestro.Usuarios import get_usuario,gets_usuarios,create_usuario,delete_usuario,update_usuario,authenticate_user

from fastapi.responses import RedirectResponse

from pydantic import BaseModel
from fastapi import HTTPException

class Token(BaseModel):
    access_token: str
    token_type: str

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuario"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SECRET_KEY = "palabra secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 540 #9 horas

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

Crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")



    
#Alta de USUARIO #Tome la decicion de usar encriptacion por si se requiere en un futuro si va a ser WEB .
@router.post("/", response_model=list[UsuarioRead])
async def Post_usuario(Usuario: UsuarioCreate, db: Session = Depends(get_db)):
    if Usuario.usuario is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El campo usuario es requerido")
    else:
         db_Usuario = get_usuario(db, usuario=Usuario.usuario)
    if db_Usuario is None:
        result = create_usuario(db=db, nombre=Usuario.nombre, usuario=Usuario.usuario, clave=Usuario.clave, email=Usuario.email)
        return result
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario Registrado anteriormente")


@router.get("/{codigo}", response_model=list[UsuarioRead]) # Lista para un solo resultado
async def get_Usuario(codigo: int, db: Session = Depends(get_db)):  
    db_Usuario = get_usuario(db, codigo=codigo, usuario=None)
    if not db_Usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    else:
        return db_Usuario

    
@router.get("/", response_model=list[UsuarioRead]) # Lista para un solo resultado
async def get_Usuarios(db: Session = Depends(get_db)):  
    db_Usuario = gets_usuarios(db)
    if not db_Usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario no encontrado")
    else:
        return [{"codigo": usuario[0], "usuario": usuario[1], "nombre": usuario[2], "email": usuario[3]} for usuario in db_Usuario]
    

@router.delete("/{codigo}", response_model=list[UsuarioRead])
async def delete_user(codigo: int, db: Session = Depends(get_db)):

    # Intenta obtener la Usuario con el código proporcionado
    db_Usuario = get_usuario(db, codigo=codigo, usuario=None) 
    # Si la Usuario no existe o es una lista vacía, lanza una excepción
    if db_Usuario is None or db_Usuario == []:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario, no existe o ya fue eliminado")
    # Si la Usuario existe, la elimina de la base de datos
    delete_usuario(db=db, codigo=codigo)
    # Devuelve la Usuario que se eliminó
    return db_Usuario


@router.put("/{codigo}", response_model=list[UsuarioRead])
async def update_Usuario(codigo: int, usuario: Usuario, db: Session = Depends(get_db)):
    # Intenta obtener la Usuario con el código proporcionado
    db_Usuario = get_usuario(db, codigo=codigo)
    # Si la Usuario no existe, lanza una excepción
    if db_Usuario is None or db_Usuario == []:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario no encontrado")
    # Si la Usuario existe, la actualiza en la base de datos
    updated_Usuario = update_usuario(db=db, codigo=codigo, usuario=usuario.usuario, clave=usuario.clave, nombre=usuario.nombre, email=usuario.email)
    # Devuelve la Usuario que se actualizó
    return updated_Usuario


#Login


@router.post("/login")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.get("username")}, expires_delta=access_token_expires
    )
    response.headers["Authorization"] = f"Bearer {access_token}"
    return RedirectResponse(url="/index", status_code=status.HTTP_303_SEE_OTHER)

def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    user = get_user_from_token(token, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_user_from_token(token: str,db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario: str = payload.get("sub")
        print(usuario)
        if usuario is None:
            raise credentials_exception
        user = get_usuario(db, codigo=None, usuario=usuario)
        print(user)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


@router.get("/user/me")
async def read_users_me(current_user: str = Depends(get_current_user)):
    print("Inicio de read_users_me")
    return {"username": current_user}

@router.get("/usuarios/ruta_protegida")
async def ruta_protegida(current_user: str = Depends(get_current_user)):
    # Tu código aquí...
    return {"message": "Esta es una ruta protegida"}
