
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from db.database import get_db, SessionLocal
from db.schemas.Maestro.Schema_Companias import Companias, CompaniasRead
from db.crud.Maestro.Crud_Companias import  create_Companias , get_Companias, gets_Companias, delete_Companias, get_Companias_nombre,update_Companias

router = APIRouter(
    prefix="/Companias",
    tags=["Companias"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/pagina", response_class=HTMLResponse)
async def read_items():
    with open('static/html/Companias.html', 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/", response_model=list[CompaniasRead])
async def routes_Post_Companias (Companias: Companias, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if Companias.id is None or Companias.nombre is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    else:
        resultado_Companias = get_Companias_nombre(db, nombre=Companias.nombre)
    if resultado_Companias is None:
        db_Companias = create_Companias(db=db, id=Companias.id, nombre=Companias.nombre, direccion=Companias.direccion, telefono=Companias.telefono, created_at=Companias.created_at, updated_at=Companias.updated_at)
        return db_Companias
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Route: nombre se encuentra registrado anteriormente en Companias ")

@router.get("/{id}", response_model=list[CompaniasRead]) 
async def routes_get_Companias_id (id: int, db: Session = Depends(get_db)):  
    db_Companias =  get_Companias(db, id=id)
    if not db_Companias:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: Companias no encontrado")
    else:
        return db_Companias
    
@router.get("/", response_model=list[CompaniasRead]) 
async def routes_gets_Companias_all (db: Session = Depends(get_db)):  
    db_Companias = gets_Companias(db)
    if not db_Companias:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: Companiass no encontrados")
    else:
        return db_Companias



@router.delete("/{id}", response_model=list[CompaniasRead]) 
async def routes_delete_Companias_numero(id: int, db: Session = Depends(get_db)):  
    resultado_Companias =  get_Companias(db, id=id)
    if not resultado_Companias:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: Companias no encontrado")
    else:
        db_Companias = delete_Companias(db, id=id)
        return db_Companias

        
@router.put("/", response_model=list[CompaniasRead]) 
async def routes_update_Companias(Companias: Companias, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if Companias.id is None or Companias.nombre is None:
        raise ValueError("Todos los campos requeridos deben tener un valor")
    else:
        resultado_codigo = get_Companias(db, codigo=Companias.id)
        if resultado_codigo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El id {Companias.id} no existe en la tabla Companias")
        else:
            resultado_Companias = get_Companias_nombre(db, descripcion=Companias.nombre)
            if resultado_Companias is None:
                db_Companias = update_Companias(db=db, id=Companias.id, nombre=Companias.nombre, direccion=Companias.direccion, telefono=Companias.telefono, created_at=Companias.created_at, updated_at=Companias.updated_at)
            else:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"La nombre {Companias.nombre} ya se encuentra en la tabla Companias")
        return db_Companias
