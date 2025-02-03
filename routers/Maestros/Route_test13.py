
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test13 import Test13Create, Test13Update, Test13Read
from db.models.test13 import Test13 as Test13Model
from db.crud.Maestro.Crud_test13 import create_test13, get_test13, gets_test13, delete_test13, update_test13
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test13",
    tags=["test13"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test13Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test13(test13: Test13Create, db: Session = Depends(get_db)):
    if test13.cod is None or test13.fecha is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test13_model = Test13Model(**test13.model_dump())
        db_test13 = create_test13(db=db, test13=test13_model)
        return Test13Read.model_validate(db_test13)
    except Exception as e:
        logger.error(f"Error al crear Test13: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{cod}", response_model=Test13Read)
async def routes_get_test13_cod(cod: int, db: Session = Depends(get_db)):
    try:
        db_test13 = get_test13(db, cod)
        if not db_test13:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test13 no encontrado")
        return Test13Read.model_validate(db_test13)
    except Exception as e:
        logger.error(f"Error al obtener Test13: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test13Read])
async def routes_gets_test13_all(db: Session = Depends(get_db)):
    try:
        db_test13 = gets_test13(db)
        if not db_test13:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test13s no encontrados")
        return [Test13Read.model_validate(test13) for test13 in db_test13]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test13: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{cod}", response_model=Test13Read)
async def routes_delete_test13_numero(cod: int, db: Session = Depends(get_db)):
    try:
        resultado_test13 = get_test13(db, cod)
        if not resultado_test13:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test13 no encontrado")
        db_test13 = delete_test13(db, cod)
        return Test13Read.model_validate(db_test13)
    except Exception as e:
        logger.error(f"Error al eliminar Test13: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{cod}", response_model=Test13Read)
async def routes_update_test13(cod: int, test13: Test13Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test13 con cod = {cod}")
    try:
        test13_data = test13.model_dump()
        db_test13 = update_test13(db=db, cod=cod, test13_data=test13_data)
        return Test13Read.model_validate(db_test13)
    except Exception as e:
        logger.error(f"Error al actualizar Test13: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test13.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
