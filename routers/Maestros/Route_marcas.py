
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from db.database import get_db, SessionLocal
from db.schemas.Maestro.Schema_marcas import marcas, marcasRead
from db.crud.Maestro.Crud_marcas import  create_marcas , get_marcas, gets_marcas, delete_marcas, get_marcas_nombre,update_marcas

router = APIRouter(
    prefix="/marcas",
    tags=["marcas"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/pagina", response_class=HTMLResponse)
async def read_items():
    with open('static/html/marcas.html', 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/", response_model=list[marcasRead])
async def routes_Post_marcas (marcas: marcas, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if marcas.codigo is None or marcas.nombre is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    else:
        resultado_marcas = get_marcas_nombre(db, nombre=marcas.nombre)
    if resultado_marcas is None:
        db_marcas = create_marcas(db=db, codigo=marcas.codigo, nombre=marcas.nombre)
        return db_marcas
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Route: nombre se encuentra registrado anteriormente en marcas ")

@router.get("/{codigo}", response_model=list[marcasRead]) 
async def routes_get_marcas_codigo (codigo: int, db: Session = Depends(get_db)):  
    db_marcas =  get_marcas(db, codigo=codigo)
    if not db_marcas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: marcas no encontrado")
    else:
        return db_marcas
    
@router.get("/", response_model=list[marcasRead]) 
async def routes_gets_marcas_all (db: Session = Depends(get_db)):  
    db_marcas = gets_marcas(db)
    if not db_marcas:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: marcass no encontrados")
    else:
        return db_marcas



@router.delete("/{codigo}", response_model=list[marcasRead]) 
async def routes_delete_marcas_numero(codigo: int, db: Session = Depends(get_db)):  
    resultado_marcas =  get_marcas(db, codigo=codigo)
    if not resultado_marcas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: marcas no encontrado")
    else:
        db_marcas = delete_marcas(db, codigo=codigo)
        return db_marcas

        
@router.put("/", response_model=list[marcasRead]) 
async def routes_update_marcas(marcas: marcas, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if marcas.codigo is None or marcas.nombre is None:
        raise ValueError("Todos los campos requeridos deben tener un valor")
    else:
        resultado_codigo = get_marcas(db, codigo=marcas.codigo)
        if resultado_codigo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El codigo {marcas.codigo} no existe en la tabla marcas")
        else:
            resultado_marcas = get_marcas_nombre(db, descripcion=marcas.nombre)
            if resultado_marcas is None:
                db_marcas = update_marcas(db=db, codigo=marcas.codigo, nombre=marcas.nombre)
            else:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"La nombre {marcas.nombre} ya se encuentra en la tabla marcas")
        return db_marcas
