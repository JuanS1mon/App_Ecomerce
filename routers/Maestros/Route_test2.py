
from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test2 import test2, test2Read
from db.crud.Maestro.Crud_test2 import create_test2, get_test2, gets_test2, delete_test2, update_test2

router = APIRouter(
    prefix="/test2",
    tags=["test2"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/pagina", response_class=HTMLResponse)
async def read_items():
    with open('static/html/test2.html', 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)


@router.get("/{campo1}", response_model=test2Read)
async def routes_get_test2_campo1(campo1: int, db: Session = Depends(get_db)):
    db_test2 = get_test2(db, campo1=campo1)
    if not db_test2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test2 no encontrado")
    return db_test2

@router.get("/", response_model=list[test2Read])
async def routes_gets_test2_all(db: Session = Depends(get_db)):
    db_test2 = gets_test2(db)
    if not db_test2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test2s no encontrados")
    return db_test2

@router.delete("/{campo1}", response_model=test2Read)
async def routes_delete_test2_numero(campo1: int, db: Session = Depends(get_db)):
    resultado_test2 = get_test2(db, campo1=campo1)
    if not resultado_test2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test2 no encontrado")
    db_test2 = delete_test2(db, campo1=campo1)
    return db_test2

@router.put("/", response_model=test2Read)
async def routes_update_test2(test2: test2, db: Session = Depends(get_db)):
    # Validaci�n de campos requeridos
    if test2.campo1 is None or test2.campo2 is None:
        raise ValueError("Todos los campos requeridos deben tener un valor")
    resultado_codigo = get_test2(db, codigo=test2.campo1)
    if resultado_codigo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El campo1 {test2.campo1} no existe en la tabla test2")
    resultado_test2 = get_test2(db, campo1=test2.campo1)
    if resultado_test2 is None:
        db_test2 = update_test2(db=db, campo1=test2.campo1, campo2=test2.campo2, campo3=test2.campo3)
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"La campo2 {test2.campo1} ya se encuentra en la tabla test2")
    return db_test2

@router.get("/count", response_model=int)
async def routes_count_test2(db: Session = Depends(get_db)):
    count = db.query(test2).count()
    return count

@router.get("/search", response_model=list[test2Read])
async def routes_search_test2(q: str, db: Session = Depends(get_db)):
    results = db.query(test2).filter(test2.campo2.contains(q)).all()
    return results

@router.get("/paginate", response_model=list[test2Read])
async def routes_paginate_test2(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    results = db.query(test2).offset(skip).limit(limit).all()
    return results
