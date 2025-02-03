
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test14 import Test14Create, Test14Update, Test14Read
from db.models.test14 import Test14 as Test14Model
from db.crud.Maestro.Crud_test14 import create_test14, get_test14, gets_test14, delete_test14, update_test14
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test14",
    tags=["test14"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test14Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test14(test14: Test14Create, db: Session = Depends(get_db)):
    if test14.codi is None or test14.valor is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test14_model = Test14Model(**test14.model_dump())
        db_test14 = create_test14(db=db, test14=test14_model)
        return Test14Read.model_validate(db_test14)
    except Exception as e:
        logger.error(f"Error al crear Test14: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{codi}", response_model=Test14Read)
async def routes_get_test14_codi(codi: int, db: Session = Depends(get_db)):
    try:
        db_test14 = get_test14(db, codi)
        if not db_test14:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test14 no encontrado")
        return Test14Read.model_validate(db_test14)
    except Exception as e:
        logger.error(f"Error al obtener Test14: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test14Read])
async def routes_gets_test14_all(db: Session = Depends(get_db)):
    try:
        db_test14 = gets_test14(db)
        if not db_test14:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test14s no encontrados")
        return [Test14Read.model_validate(test14) for test14 in db_test14]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test14: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{codi}", response_model=Test14Read)
async def routes_delete_test14_numero(codi: int, db: Session = Depends(get_db)):
    try:
        resultado_test14 = get_test14(db, codi)
        if not resultado_test14:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test14 no encontrado")
        db_test14 = delete_test14(db, codi)
        return Test14Read.model_validate(db_test14)
    except Exception as e:
        logger.error(f"Error al eliminar Test14: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{codi}", response_model=Test14Read)
async def routes_update_test14(codi: int, test14: Test14Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test14 con codi = {codi}")
    try:
        test14_data = test14.model_dump()
        db_test14 = update_test14(db=db, codi=codi, test14_data=test14_data)
        return Test14Read.model_validate(db_test14)
    except Exception as e:
        logger.error(f"Error al actualizar Test14: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test14.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
