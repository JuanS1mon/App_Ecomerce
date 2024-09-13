
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from db.database import get_db, SessionLocal
from db.schemas.Maestro.Schema_test1 import test1, test1Read
from db.crud.Maestro.Crud_test1 import  create_test1 , get_test1, gets_test1, delete_test1, get_test1_campo1,update_test1

router = APIRouter(
    prefix="/test1",
    tags=["test1"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/pagina", response_class=HTMLResponse)
async def read_items():
    with open('static/html/test1.html', 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/", response_model=list[test1Read])
async def routes_Post_test1 (test1: test1, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if test1.id is None or test1.campo1 is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    else:
        resultado_test1 = get_test1_campo1(db, campo1=test1.campo1)
    if resultado_test1 is None:
        db_test1 = create_test1(db=db, id=test1.id, campo1=test1.campo1, campo2=test1.campo2, campo3=test1.campo3)
        return db_test1
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Route: campo1 se encuentra registrado anteriormente en test1 ")

@router.get("/{id}", response_model=list[test1Read]) 
async def routes_get_test1_id (id: int, db: Session = Depends(get_db)):  
    db_test1 =  get_test1(db, id=id)
    if not db_test1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test1 no encontrado")
    else:
        return db_test1
    
@router.get("/", response_model=list[test1Read]) 
async def routes_gets_test1_all (db: Session = Depends(get_db)):  
    db_test1 = gets_test1(db)
    if not db_test1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test1s no encontrados")
    else:
        return db_test1



@router.delete("/{id}", response_model=list[test1Read]) 
async def routes_delete_test1_numero(id: int, db: Session = Depends(get_db)):  
    resultado_test1 =  get_test1(db, id=id)
    if not resultado_test1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test1 no encontrado")
    else:
        db_test1 = delete_test1(db, id=id)
        return db_test1

        
@router.put("/", response_model=list[test1Read]) 
async def routes_update_test1(test1: test1, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if test1.id is None or test1.campo1 is None:
        raise ValueError("Todos los campos requeridos deben tener un valor")
    else:
        resultado_codigo = get_test1(db, codigo=test1.id)
        if resultado_codigo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El id {test1.id} no existe en la tabla test1")
        else:
            resultado_test1 = get_test1_campo1(db, descripcion=test1.campo1)
            if resultado_test1 is None:
                db_test1 = update_test1(db=db, id=test1.id, campo1=test1.campo1, campo2=test1.campo2, campo3=test1.campo3)
            else:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"La campo1 {test1.campo1} ya se encuentra en la tabla test1")
        return db_test1
