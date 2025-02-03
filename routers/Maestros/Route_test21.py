
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test21 import Test21Create, Test21Update, Test21Read
from db.models.test21 import Test21 as Test21Model
from db.crud.Maestro.Crud_test21 import create_test21, get_test21, gets_test21, delete_test21, update_test21
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test21",
    tags=["test21"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test21Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test21(test21: Test21Create, db: Session = Depends(get_db)):
    if test21.codi is None or test21.test1 is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test21_model = Test21Model(**test21.model_dump())
        db_test21 = create_test21(db=db, test21=test21_model)
        return Test21Read.model_validate(db_test21)
    except Exception as e:
        logger.error(f"Error al crear Test21: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{codi}", response_model=Test21Read)
async def routes_get_test21_codi(codi: int, db: Session = Depends(get_db)):
    try:
        db_test21 = get_test21(db, codi)
        if not db_test21:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test21 no encontrado")
        return Test21Read.model_validate(db_test21)
    except Exception as e:
        logger.error(f"Error al obtener Test21: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test21Read])
async def routes_gets_test21_all(db: Session = Depends(get_db)):
    try:
        db_test21 = gets_test21(db)
        if not db_test21:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test21s no encontrados")
        return [Test21Read.model_validate(test21) for test21 in db_test21]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test21: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{codi}", response_model=Test21Read)
async def routes_delete_test21_numero(codi: int, db: Session = Depends(get_db)):
    try:
        resultado_test21 = get_test21(db, codi)
        if not resultado_test21:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test21 no encontrado")
        db_test21 = delete_test21(db, codi)
        return Test21Read.model_validate(db_test21)
    except Exception as e:
        logger.error(f"Error al eliminar Test21: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{codi}", response_model=Test21Read)
async def routes_update_test21(codi: int, test21: Test21Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test21 con codi = {codi}")
    try:
        test21_data = test21.model_dump()
        db_test21 = update_test21(db=db, codi=codi, test21_data=test21_data)
        return Test21Read.model_validate(db_test21)
    except Exception as e:
        logger.error(f"Error al actualizar Test21: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test21.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
