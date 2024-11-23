
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from db.database import get_db, SessionLocal
from db.schemas.Maestro.Schema_usuario import usuario, usuarioRead
from db.crud.Maestro.Crud_usuario import  create_usuario , get_usuario, gets_usuario, delete_usuario, get_usuario_username,update_usuario

router = APIRouter(
    prefix="/usuario",
    tags=["usuario"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/pagina", response_class=HTMLResponse)
async def read_items():
    with open('static/html/usuario.html', 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/", response_model=list[usuarioRead])
async def routes_Post_usuario (usuario: usuario, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if usuario.id is None or usuario.username is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    else:
        resultado_usuario = get_usuario_username(db, username=usuario.username)
    if resultado_usuario is None:
        db_usuario = create_usuario(db=db, id=usuario.id, username=usuario.username, email=usuario.email, password_hash=usuario.password_hash, created_at=usuario.created_at, updated_at=usuario.updated_at)
        return db_usuario
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Route: username se encuentra registrado anteriormente en usuario ")

@router.get("/{id}", response_model=list[usuarioRead]) 
async def routes_get_usuario_id (id: int, db: Session = Depends(get_db)):  
    db_usuario =  get_usuario(db, id=id)
    if not db_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: usuario no encontrado")
    else:
        return db_usuario
    
@router.get("/", response_model=list[usuarioRead]) 
async def routes_gets_usuario_all (db: Session = Depends(get_db)):  
    db_usuario = gets_usuario(db)
    if not db_usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: usuarios no encontrados")
    else:
        return db_usuario



@router.delete("/{id}", response_model=list[usuarioRead]) 
async def routes_delete_usuario_numero(id: int, db: Session = Depends(get_db)):  
    resultado_usuario =  get_usuario(db, id=id)
    if not resultado_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: usuario no encontrado")
    else:
        db_usuario = delete_usuario(db, id=id)
        return db_usuario

        
@router.put("/", response_model=list[usuarioRead]) 
async def routes_update_usuario(usuario: usuario, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if usuario.id is None or usuario.username is None:
        raise ValueError("Todos los campos requeridos deben tener un valor")
    else:
        resultado_codigo = get_usuario(db, codigo=usuario.id)
        if resultado_codigo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El id {usuario.id} no existe en la tabla usuario")
        else:
            resultado_usuario = get_usuario_username(db, descripcion=usuario.username)
            if resultado_usuario is None:
                db_usuario = update_usuario(db=db, id=usuario.id, username=usuario.username, email=usuario.email, password_hash=usuario.password_hash, created_at=usuario.created_at, updated_at=usuario.updated_at)
            else:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"La username {usuario.username} ya se encuentra en la tabla usuario")
        return db_usuario
