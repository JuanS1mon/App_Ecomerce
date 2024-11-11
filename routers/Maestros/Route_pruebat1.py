from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_pruebat1 import Pruebat1Create, Pruebat1Update, Pruebat1Read
from db.models.pruebat1 import Pruebat1 as Pruebat1Model
from db.crud.Maestro.Crud_pruebat1 import create_pruebat1, get_pruebat1, gets_pruebat1, delete_pruebat1, update_pruebat1
from fastapi.responses import HTMLResponse, FileResponse

router = APIRouter(
    prefix="/pruebat1",
    tags=["pruebat1"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Pruebat1Read)
async def routes_post_pruebat1(pruebat1: Pruebat1Create, db: Session = Depends(get_db)):

    # Validación de campos requeridos
    if pruebat1.campot1 is None or pruebat1.campot2 is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    pruebat1_model = Pruebat1Model(**pruebat1.model_dump())
    db_pruebat1 = create_pruebat1(db=db, pruebat1=pruebat1_model)
    return Pruebat1Read.model_validate(db_pruebat1)


@router.get("/id/{campot1}", response_model=Pruebat1Read)
async def routes_get_pruebat1_campo1(campot1: int, db: Session = Depends(get_db)):
    db_pruebat1 = get_pruebat1(db, campot1)
    if not db_pruebat1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: pruebat1 no encontrado")
    return Pruebat1Read.model_validate(db_pruebat1)

@router.get("/", response_model=list[Pruebat1Read])
async def routes_gets_pruebat1_all(db: Session = Depends(get_db)):
    db_pruebat1 = gets_pruebat1(db)
    if not db_pruebat1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: pruebat1s no encontrados")
    return [Pruebat1Read.model_validate(pruebat1) for pruebat1 in db_pruebat1]

@router.delete("/id/{campot1}", response_model=Pruebat1Read)
async def routes_delete_pruebat1_numero(campot1: int, db: Session = Depends(get_db)):
    resultado_pruebat1 = get_pruebat1(db, campot1)
    if not resultado_pruebat1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: pruebat1 no encontrado")
    db_pruebat1 = delete_pruebat1(db, campot1)
    return Pruebat1Read.model_validate(db_pruebat1)


@router.put("/id/{campot1}", response_model=Pruebat1Read)
async def routes_update_pruebat1(campot1: int, pruebat1: Pruebat1Update, db: Session = Depends(get_db)):
    print(f"Actualizando pruebat1 con campot1 = {campot1}")
    # Convertir el objeto Pydantic a diccionario
    pruebat1_data = pruebat1.model_dump()

    # Actualizar el registro existente
    db_pruebat1 = update_pruebat1(db=db, campot1=campot1, pruebat1_data=pruebat1_data)
    return Pruebat1Read.model_validate(db_pruebat1)

@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    with open("static/html/pruebat1.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)
