from fastapi import APIRouter, HTTPException, status, Depends, Path
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test1 import Test1, Test1Read
from db.crud.Maestro.Crud_test1 import (create_test1,get_test1_by_campo1,gets_test1,delete_test1,update_test1)

router = APIRouter(
    prefix="/test1",
    tags=["test1"],
    responses={404: {"description": "Ruta no encontrada"}},
)

@router.post("/", response_model=Test1Read)
async def routes_post_test1(test1: Test1, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if test1.campo1 is None or test1.campo2 is None:
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="Todos los campos requeridos deben tener un valor"
        )
    resultado_test1 = get_test1_by_campo1(db, campo1=test1.campo1)
    if resultado_test1 is None:
        db_test1 = create_test1(
            db=db,
            campo1=test1.campo1,
            campo2=test1.campo2,
            campo3=test1.campo3,
            campo4=test1.campo4
        )
        return db_test1
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Route: campo1 se encuentra registrado anteriormente en test1"
        )

# Ruta estática primero
@router.get("/", response_model=list[Test1Read])
async def routes_gets_test1_all(db: Session = Depends(get_db)):
    db_test1 = gets_test1(db)
    if not db_test1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Route: test1s no encontrados"
        )
    return db_test1

# Ruta dinámica después
@router.get("/{campo1}", response_model=Test1Read)
async def routes_get_test1_campo1(
    campo1: int = Path(..., title="Campo1", description="Debe ser un entero"),
    db: Session = Depends(get_db)
):
    db_test1 = get_test1_by_campo1(db, campo1=campo1)
    if not db_test1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route: test1 no encontrado"
        )
    return db_test1

@router.delete("/{campo1}", response_model=Test1Read)
async def routes_delete_test1_numero(
    campo1: int,
    db: Session = Depends(get_db)
):
    resultado_test1 = get_test1_by_campo1(db, campo1=campo1)
    if not resultado_test1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route: test1 no encontrado"
        )
    db_test1 = delete_test1(db, campo1=campo1)
    return db_test1

@router.put("/", response_model=Test1Read)
async def routes_update_test1(test1: Test1, db: Session = Depends(get_db)):
    # Validación de campos requeridos
    if test1.campo1 is None or test1.campo2 is None:
        raise ValueError("Todos los campos requeridos deben tener un valor")
    resultado_codigo = get_test1_by_campo1(db, campo1=test1.campo1)
    if resultado_codigo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El campo1 {test1.campo1} no existe en la tabla test1"
        )
    db_test1 = update_test1(
        db=db,
        campo1=test1.campo1,
        campo2=test1.campo2,
        campo3=test1.campo3,
        campo4=test1.campo4
    )
    return db_test1