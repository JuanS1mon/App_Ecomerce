
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from db.database import get_db, SessionLocal
from db.schemas.Maestro.Schema_rrr import rrr, rrrRead
from db.crud.Maestro.Crud_rrr import  create_rrr , get_rrr, gets_rrr, delete_rrr, get_rrr_descripcion,update_rrr

router = APIRouter(
    prefix="/rrr",
    tags=["rrr"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/pagina", response_class=HTMLResponse)
async def read_items():
    with open('static/html/rrr.html', 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/", response_model=list[rrrRead])
async def routes_Post_rrr (rrr: rrr, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if rrr.codigo is None or rrr.descripcion is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    else:
        resultado_rrr = get_rrr_descripcion(db, descripcion=rrr.descripcion)
    if resultado_rrr is None:
        db_rrr = create_rrr(db=db, codigo=rrr.codigo, descripcion=rrr.descripcion)
        return db_rrr
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Route: descripcion se encuentra registrado anteriormente en rrr ")

@router.get("/{codigo}", response_model=list[rrrRead]) 
async def routes_get_rrr_codigo (codigo: int, db: Session = Depends(get_db)):  
    db_rrr =  get_rrr(db, codigo=codigo)
    if not db_rrr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: rrr no encontrado")
    else:
        return db_rrr
    
@router.get("/", response_model=list[rrrRead]) 
async def routes_gets_rrr_all (db: Session = Depends(get_db)):  
    db_rrr = gets_rrr(db)
    if not db_rrr:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: rrrs no encontrados")
    else:
        return db_rrr



@router.delete("/{codigo}", response_model=list[rrrRead]) 
async def routes_delete_rrr_numero(codigo: int, db: Session = Depends(get_db)):  
    resultado_rrr =  get_rrr(db, codigo=codigo)
    if not resultado_rrr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: rrr no encontrado")
    else:
        db_rrr = delete_rrr(db, codigo=codigo)
        return db_rrr

        
@router.put("/", response_model=list[rrrRead]) 
async def routes_update_rrr(rrr: rrr, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if rrr.codigo is None or rrr.descripcion is None:
        raise ValueError("Todos los campos requeridos deben tener un valor")
    else:
        resultado_codigo = get_rrr(db, codigo=rrr.codigo)
        if resultado_codigo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El codigo {rrr.codigo} no existe en la tabla rrr")
        else:
            resultado_rrr = get_rrr_descripcion(db, descripcion=rrr.descripcion)
            if resultado_rrr is None:
                db_rrr = update_rrr(db=db, codigo=rrr.codigo, descripcion=rrr.descripcion)
            else:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"La descripcion {rrr.descripcion} ya se encuentra en la tabla rrr")
        return db_rrr
