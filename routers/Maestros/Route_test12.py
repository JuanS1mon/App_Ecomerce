
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test12 import Test12Create, Test12Update, Test12Read
from db.models.test12 import Test12 as Test12Model
from db.crud.Maestro.Crud_test12 import create_test12, get_test12, gets_test12, delete_test12, update_test12
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test12",
    tags=["test12"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test12Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test12(test12: Test12Create, db: Session = Depends(get_db)):
    if test12.cod is None or test12.descri is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test12_model = Test12Model(**test12.model_dump())
        db_test12 = create_test12(db=db, test12=test12_model)
        return Test12Read.model_validate(db_test12)
    except Exception as e:
        logger.error(f"Error al crear Test12: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{cod}", response_model=Test12Read)
async def routes_get_test12_cod(cod: int, db: Session = Depends(get_db)):
    try:
        db_test12 = get_test12(db, cod)
        if not db_test12:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test12 no encontrado")
        return Test12Read.model_validate(db_test12)
    except Exception as e:
        logger.error(f"Error al obtener Test12: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test12Read])
async def routes_gets_test12_all(db: Session = Depends(get_db)):
    try:
        db_test12 = gets_test12(db)
        if not db_test12:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test12s no encontrados")
        return [Test12Read.model_validate(test12) for test12 in db_test12]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test12: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{cod}", response_model=Test12Read)
async def routes_delete_test12_numero(cod: int, db: Session = Depends(get_db)):
    try:
        resultado_test12 = get_test12(db, cod)
        if not resultado_test12:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test12 no encontrado")
        db_test12 = delete_test12(db, cod)
        return Test12Read.model_validate(db_test12)
    except Exception as e:
        logger.error(f"Error al eliminar Test12: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{cod}", response_model=Test12Read)
async def routes_update_test12(cod: int, test12: Test12Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test12 con cod = {cod}")
    try:
        test12_data = test12.model_dump()
        db_test12 = update_test12(db=db, cod=cod, test12_data=test12_data)
        return Test12Read.model_validate(db_test12)
    except Exception as e:
        logger.error(f"Error al actualizar Test12: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test12.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
