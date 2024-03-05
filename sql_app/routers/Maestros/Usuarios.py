from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from db.database import  get_db
from db.schemas.Maestro.Usuarios import UsuarioCreate,Usuario,UsuarioRead,LoginForm
from db.crud.Maestro.Usuarios import get_usuario,gets_usuarios,create_usuario,delete_usuario,update_usuario,authenticate_user

from fastapi.responses import RedirectResponse


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuario"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)


@router.post("/", response_model=list[UsuarioRead])
async def Post_usuario(Usuario: UsuarioCreate, db: Session = Depends(get_db)):
    if Usuario.usuario is None:
        raise HTTPException(status_code=400, detail="El campo usuario es requerido")
    else:
         db_Usuario = get_usuario(db, usuario=Usuario.usuario)
    if db_Usuario is None:
        result = create_usuario(db=db, nombre=Usuario.nombre, usuario=Usuario.usuario, clave=Usuario.clave, email=Usuario.email)
        return result
    else:
        raise HTTPException(status_code=402, detail="Usuario Registrado anteriormente")


@router.get("/{codigo}", response_model=list[UsuarioRead]) # Lista para un solo resultado
async def get_Usuario(codigo: int, db: Session = Depends(get_db)):  
    db_Usuario = get_usuario(db, codigo=codigo, usuario=None)
    if not db_Usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    else:
        return db_Usuario

    
@router.get("/", response_model=list[UsuarioRead]) # Lista para un solo resultado
async def get_Usuarios(db: Session = Depends(get_db)):  
    db_Usuario = gets_usuarios(db)
    if not db_Usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    else:
        return [{"codigo": usuario[0], "usuario": usuario[1], "nombre": usuario[2], "email": usuario[3]} for usuario in db_Usuario]
    

@router.delete("/{codigo}", response_model=list[UsuarioRead])
async def delete_Usuario(codigo: int, db: Session = Depends(get_db)):
    # Intenta obtener la Usuario con el código proporcionado
    db_Usuario = get_usuario(db, codigo=codigo, usuario=None) 
    # Si la Usuario no existe o es una lista vacía, lanza una excepción
    if db_Usuario is None or db_Usuario == []:
        raise HTTPException(status_code=404, detail="El usuario, no existe o ya fue eliminado")
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
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    # Si la Usuario existe, la actualiza en la base de datos
    updated_Usuario = update_usuario(db=db, codigo=codigo, usuario=usuario.usuario, clave=usuario.clave, nombre=usuario.nombre, email=usuario.email)
    # Devuelve la Usuario que se actualizó
    return updated_Usuario







@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = authenticate_user(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Si la autenticación es exitosa, redirige al usuario
    response = RedirectResponse(url='/static/index.html', status_code=status.HTTP_303_SEE_OTHER)
    return response
    #FALTA 
    # Aquí deberías generar y devolver un token de acceso
    # ...import jwt
    '''
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta

SECRET_KEY = "tu_clave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = authenticate_user(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": usuario.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
    '''