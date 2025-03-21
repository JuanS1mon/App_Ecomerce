
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_a1 import A1Create, A1Update, A1Read
from db.models.a1 import A1 as A1Model
from db.crud.Maestro.Crud_a1 import create_a1, get_a1, gets_a1, delete_a1, update_a1
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/a1",
    tags=["a1"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=A1Read, status_code=status.HTTP_201_CREATED)
async def routes_post_a1(a1: A1Create, db: Session = Depends(get_db)):
    if a1.a is None or a1.b is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        a1_model = A1Model(**a1.model_dump())
        db_a1 = create_a1(db=db, a1=a1_model)
        return A1Read.model_validate(db_a1)
    except Exception as e:
        logger.error(f"Error al crear A1: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{a}", response_model=A1Read)
async def routes_get_a1_a(a: int, db: Session = Depends(get_db)):
    try:
        db_a1 = get_a1(db, a)
        if not db_a1:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: a1 no encontrado")
        return A1Read.model_validate(db_a1)
    except Exception as e:
        logger.error(f"Error al obtener A1: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[A1Read])
async def routes_gets_a1_all(db: Session = Depends(get_db)):
    try:
        db_a1 = gets_a1(db)
        if not db_a1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: a1s no encontrados")
        return [A1Read.model_validate(a1) for a1 in db_a1]
    except Exception as e:
        logger.error(f"Error al obtener registros de A1: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{a}", response_model=A1Read)
async def routes_delete_a1_numero(a: int, db: Session = Depends(get_db)):
    try:
        resultado_a1 = get_a1(db, a)
        if not resultado_a1:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: a1 no encontrado")
        db_a1 = delete_a1(db, a)
        return A1Read.model_validate(db_a1)
    except Exception as e:
        logger.error(f"Error al eliminar A1: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{a}", response_model=A1Read)
async def routes_update_a1(a: int, a1: A1Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando A1 con a = {a}")
    try:
        a1_data = a1.model_dump()
        db_a1 = update_a1(db=db, a=a, a1_data=a1_data)
        return A1Read.model_validate(db_a1)
    except Exception as e:
        logger.error(f"Error al actualizar A1: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/a1.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
