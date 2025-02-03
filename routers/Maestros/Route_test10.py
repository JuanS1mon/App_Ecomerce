
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test10 import Test10Create, Test10Update, Test10Read
from db.models.test10 import Test10 as Test10Model
from db.crud.Maestro.Crud_test10 import create_test10, get_test10, gets_test10, delete_test10, update_test10
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test10",
    tags=["test10"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test10Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test10(test10: Test10Create, db: Session = Depends(get_db)):
    if test10.codigo is None or test10.fecha is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test10_model = Test10Model(**test10.model_dump())
        db_test10 = create_test10(db=db, test10=test10_model)
        return Test10Read.model_validate(db_test10)
    except Exception as e:
        logger.error(f"Error al crear Test10: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{codigo}", response_model=Test10Read)
async def routes_get_test10_codigo(codigo: int, db: Session = Depends(get_db)):
    try:
        db_test10 = get_test10(db, codigo)
        if not db_test10:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test10 no encontrado")
        return Test10Read.model_validate(db_test10)
    except Exception as e:
        logger.error(f"Error al obtener Test10: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test10Read])
async def routes_gets_test10_all(db: Session = Depends(get_db)):
    try:
        db_test10 = gets_test10(db)
        if not db_test10:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test10s no encontrados")
        return [Test10Read.model_validate(test10) for test10 in db_test10]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test10: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{codigo}", response_model=Test10Read)
async def routes_delete_test10_numero(codigo: int, db: Session = Depends(get_db)):
    try:
        resultado_test10 = get_test10(db, codigo)
        if not resultado_test10:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test10 no encontrado")
        db_test10 = delete_test10(db, codigo)
        return Test10Read.model_validate(db_test10)
    except Exception as e:
        logger.error(f"Error al eliminar Test10: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{codigo}", response_model=Test10Read)
async def routes_update_test10(codigo: int, test10: Test10Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test10 con codigo = {codigo}")
    try:
        test10_data = test10.model_dump()
        db_test10 = update_test10(db=db, codigo=codigo, test10_data=test10_data)
        return Test10Read.model_validate(db_test10)
    except Exception as e:
        logger.error(f"Error al actualizar Test10: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test10.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
