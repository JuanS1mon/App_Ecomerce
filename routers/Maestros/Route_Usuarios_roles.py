
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from db.database import get_db, SessionLocal
from db.schemas.Maestro.Schema_Usuarios_roles import Usuarios_roles, Usuarios_rolesRead
from db.crud.Maestro.Crud_Usuarios_roles import  create_Usuarios_roles , get_Usuarios_roles, gets_Usuarios_roles, delete_Usuarios_roles, get_Usuarios_roles_usuario_id,update_Usuarios_roles

router = APIRouter(
    prefix="/Usuarios_roles",
    tags=["Usuarios_roles"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/pagina", response_class=HTMLResponse)
async def read_items():
    with open('static/html/Usuarios_roles.html', 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/", response_model=list[Usuarios_rolesRead])
async def routes_Post_Usuarios_roles (Usuarios_roles: Usuarios_roles, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if Usuarios_roles.id is None or Usuarios_roles.usuario_id is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    else:
        resultado_Usuarios_roles = get_Usuarios_roles_usuario_id(db, usuario_id=Usuarios_roles.usuario_id)
    if resultado_Usuarios_roles is None:
        db_Usuarios_roles = create_Usuarios_roles(db=db, id=Usuarios_roles.id, usuario_id=Usuarios_roles.usuario_id, empresa_id=Usuarios_roles.empresa_id, rol=Usuarios_roles.rol, created_at=Usuarios_roles.created_at, updated_at=Usuarios_roles.updated_at)
        return db_Usuarios_roles
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Route: usuario_id se encuentra registrado anteriormente en Usuarios_roles ")

@router.get("/{id}", response_model=list[Usuarios_rolesRead]) 
async def routes_get_Usuarios_roles_id (id: int, db: Session = Depends(get_db)):  
    db_Usuarios_roles =  get_Usuarios_roles(db, id=id)
    if not db_Usuarios_roles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: Usuarios_roles no encontrado")
    else:
        return db_Usuarios_roles
    
@router.get("/", response_model=list[Usuarios_rolesRead]) 
async def routes_gets_Usuarios_roles_all (db: Session = Depends(get_db)):  
    db_Usuarios_roles = gets_Usuarios_roles(db)
    if not db_Usuarios_roles:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: Usuarios_roless no encontrados")
    else:
        return db_Usuarios_roles



@router.delete("/{id}", response_model=list[Usuarios_rolesRead]) 
async def routes_delete_Usuarios_roles_numero(id: int, db: Session = Depends(get_db)):  
    resultado_Usuarios_roles =  get_Usuarios_roles(db, id=id)
    if not resultado_Usuarios_roles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: Usuarios_roles no encontrado")
    else:
        db_Usuarios_roles = delete_Usuarios_roles(db, id=id)
        return db_Usuarios_roles

        
@router.put("/", response_model=list[Usuarios_rolesRead]) 
async def routes_update_Usuarios_roles(Usuarios_roles: Usuarios_roles, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if Usuarios_roles.id is None or Usuarios_roles.usuario_id is None:
        raise ValueError("Todos los campos requeridos deben tener un valor")
    else:
        resultado_codigo = get_Usuarios_roles(db, codigo=Usuarios_roles.id)
        if resultado_codigo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El id {Usuarios_roles.id} no existe en la tabla Usuarios_roles")
        else:
            resultado_Usuarios_roles = get_Usuarios_roles_usuario_id(db, descripcion=Usuarios_roles.usuario_id)
            if resultado_Usuarios_roles is None:
                db_Usuarios_roles = update_Usuarios_roles(db=db, id=Usuarios_roles.id, usuario_id=Usuarios_roles.usuario_id, empresa_id=Usuarios_roles.empresa_id, rol=Usuarios_roles.rol, created_at=Usuarios_roles.created_at, updated_at=Usuarios_roles.updated_at)
            else:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"La usuario_id {Usuarios_roles.usuario_id} ya se encuentra en la tabla Usuarios_roles")
        return db_Usuarios_roles
