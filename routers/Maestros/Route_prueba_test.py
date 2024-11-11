
from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_prueba_test import prueba_test, prueba_testRead
from db.crud.Maestro.Crud_prueba_test import create_prueba_test, get_prueba_test, get_prueba_test_by_campo1, gets_prueba_test, delete_prueba_test, update_prueba_test

router = APIRouter(
    prefix="/prueba_test",
    tags=["prueba_test"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/pagina", response_class=HTMLResponse)
async def read_items():
    with open('static/html/prueba_test.html', 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/", response_model=prueba_testRead)
async def routes_post_prueba_test(prueba_test: prueba_test, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if prueba_test.campo1 is None or prueba_test.campostr is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    resultado_prueba_test = get_prueba_test_by_campo1(db, campostr=prueba_test.campo1)
    if resultado_prueba_test is None:
        db_prueba_test = create_prueba_test(db=db, campo1=prueba_test.campo1, campostr=prueba_test.campostr, campofloat=prueba_test.campofloat)
        return db_prueba_test
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Route: campostr se encuentra registrado anteriormente en prueba_test")

@router.get("/{campo1}", response_model=prueba_testRead)
async def routes_get_prueba_test_campo1(campo1: int, db: Session = Depends(get_db)):
    db_prueba_test = get_prueba_test(db, campo1=campo1)
    if not db_prueba_test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: prueba_test no encontrado")
    return db_prueba_test

@router.get("/", response_model=list[prueba_testRead])
async def routes_gets_prueba_test_all(db: Session = Depends(get_db)):
    db_prueba_test = gets_prueba_test(db)
    if not db_prueba_test:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: prueba_tests no encontrados")
    return db_prueba_test

@router.delete("/{campo1}", response_model=prueba_testRead)
async def routes_delete_prueba_test_numero(campo1: int, db: Session = Depends(get_db)):
    resultado_prueba_test = get_prueba_test(db, campo1=campo1)
    if not resultado_prueba_test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: prueba_test no encontrado")
    db_prueba_test = delete_prueba_test(db, campo1=campo1)
    return db_prueba_test

@router.put("/", response_model=prueba_testRead)
async def routes_update_prueba_test(prueba_test: prueba_test, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if prueba_test.campo1 is None or prueba_test.campostr is None:
        raise ValueError("Todos los campos requeridos deben tener un valor")
    resultado_codigo = get_prueba_test(db, codigo=prueba_test.campo1)
    if resultado_codigo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El campo1 {prueba_test.campo1} no existe en la tabla prueba_test")
    resultado_prueba_test = get_prueba_test_by_campo1(db, campostr=prueba_test.campostr)
    if resultado_prueba_test is None:
        db_prueba_test = update_prueba_test(db=db, campo1=prueba_test.campo1, campostr=prueba_test.campostr, campofloat=prueba_test.campofloat)
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"La campostr {prueba_test.campo1} ya se encuentra en la tabla prueba_test")
    return db_prueba_test

@router.get("/count", response_model=int)
async def routes_count_prueba_test(db: Session = Depends(get_db)):
    count = db.query(prueba_test).count()
    return count

@router.get("/search", response_model=list[prueba_testRead])
async def routes_search_prueba_test(q: str, db: Session = Depends(get_db)):
    results = db.query(prueba_test).filter(prueba_test.campostr.contains(q)).all()
    return results

@router.get("/paginate", response_model=list[prueba_testRead])
async def routes_paginate_prueba_test(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    results = db.query(prueba_test).offset(skip).limit(limit).all()
    return results
