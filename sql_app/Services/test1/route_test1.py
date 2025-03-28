
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from .schema_test1 import Test1Create, Test1Update, Test1Read
from .model_test1 import Test1 as Test1Model
from .service_test1 import create_test1, get_test1, gets_test1, delete_test1, update_test1
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test1",
    tags=["test1"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test1Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test1(test1: Test1Create, db: Session = Depends(get_db)):
    if test1.id is None or test1.test1 is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test1_model = Test1Model(**test1.model_dump())
        db_test1 = create_test1(db=db, test1=test1_model)
        return Test1Read.model_validate(db_test1)
    except Exception as e:
        logger.error(f"Error al crear Test1: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=Test1Read)
async def routes_get_test1_id(id: str, db: Session = Depends(get_db)):
    try:
        db_test1 = get_test1(db, id)
        if not db_test1:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test1 no encontrado")
        return Test1Read.model_validate(db_test1)
    except Exception as e:
        logger.error(f"Error al obtener Test1: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test1Read])
async def routes_gets_test1_all(db: Session = Depends(get_db)):
    try:
        db_test1 = gets_test1(db)
        if not db_test1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test1s no encontrados")
        return [Test1Read.model_validate(test1) for test1 in db_test1]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test1: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=Test1Read)
async def routes_delete_test1_numero(id: str, db: Session = Depends(get_db)):
    try:
        resultado_test1 = get_test1(db, id)
        if not resultado_test1:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test1 no encontrado")
        db_test1 = delete_test1(db, id)
        return Test1Read.model_validate(db_test1)
    except Exception as e:
        logger.error(f"Error al eliminar Test1: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=Test1Read)
async def routes_update_test1(id: str, test1: Test1Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test1 con id = {id}")
    try:
        test1_data = test1.model_dump()
        db_test1 = update_test1(db=db, id=id, test1_data=test1_data)
        return Test1Read.model_validate(db_test1)
    except Exception as e:
        logger.error(f"Error al actualizar Test1: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Considerar si quieres cambiar la ubicación HTML para servicios
        with open("static/html/test1.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
