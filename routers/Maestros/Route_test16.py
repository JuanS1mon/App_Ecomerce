
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test16 import Test16Create, Test16Update, Test16Read
from db.models.test16 import Test16 as Test16Model
from db.crud.Maestro.Crud_test16 import create_test16, get_test16, gets_test16, delete_test16, update_test16
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test16",
    tags=["test16"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test16Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test16(test16: Test16Create, db: Session = Depends(get_db)):
    if test16.codi is None or test16.dns is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test16_model = Test16Model(**test16.model_dump())
        db_test16 = create_test16(db=db, test16=test16_model)
        return Test16Read.model_validate(db_test16)
    except Exception as e:
        logger.error(f"Error al crear Test16: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{codi}", response_model=Test16Read)
async def routes_get_test16_codi(codi: int, db: Session = Depends(get_db)):
    try:
        db_test16 = get_test16(db, codi)
        if not db_test16:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test16 no encontrado")
        return Test16Read.model_validate(db_test16)
    except Exception as e:
        logger.error(f"Error al obtener Test16: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test16Read])
async def routes_gets_test16_all(db: Session = Depends(get_db)):
    try:
        db_test16 = gets_test16(db)
        if not db_test16:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test16s no encontrados")
        return [Test16Read.model_validate(test16) for test16 in db_test16]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test16: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{codi}", response_model=Test16Read)
async def routes_delete_test16_numero(codi: int, db: Session = Depends(get_db)):
    try:
        resultado_test16 = get_test16(db, codi)
        if not resultado_test16:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test16 no encontrado")
        db_test16 = delete_test16(db, codi)
        return Test16Read.model_validate(db_test16)
    except Exception as e:
        logger.error(f"Error al eliminar Test16: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{codi}", response_model=Test16Read)
async def routes_update_test16(codi: int, test16: Test16Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test16 con codi = {codi}")
    try:
        test16_data = test16.model_dump()
        db_test16 = update_test16(db=db, codi=codi, test16_data=test16_data)
        return Test16Read.model_validate(db_test16)
    except Exception as e:
        logger.error(f"Error al actualizar Test16: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test16.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
