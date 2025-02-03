
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test18 import Test18Create, Test18Update, Test18Read
from db.models.test18 import Test18 as Test18Model
from db.crud.Maestro.Crud_test18 import create_test18, get_test18, gets_test18, delete_test18, update_test18
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test18",
    tags=["test18"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test18Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test18(test18: Test18Create, db: Session = Depends(get_db)):
    if test18.id is None or test18.fecha is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test18_model = Test18Model(**test18.model_dump())
        db_test18 = create_test18(db=db, test18=test18_model)
        return Test18Read.model_validate(db_test18)
    except Exception as e:
        logger.error(f"Error al crear Test18: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=Test18Read)
async def routes_get_test18_id(id: int, db: Session = Depends(get_db)):
    try:
        db_test18 = get_test18(db, id)
        if not db_test18:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test18 no encontrado")
        return Test18Read.model_validate(db_test18)
    except Exception as e:
        logger.error(f"Error al obtener Test18: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test18Read])
async def routes_gets_test18_all(db: Session = Depends(get_db)):
    try:
        db_test18 = gets_test18(db)
        if not db_test18:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test18s no encontrados")
        return [Test18Read.model_validate(test18) for test18 in db_test18]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test18: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=Test18Read)
async def routes_delete_test18_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_test18 = get_test18(db, id)
        if not resultado_test18:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test18 no encontrado")
        db_test18 = delete_test18(db, id)
        return Test18Read.model_validate(db_test18)
    except Exception as e:
        logger.error(f"Error al eliminar Test18: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=Test18Read)
async def routes_update_test18(id: int, test18: Test18Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test18 con id = {id}")
    try:
        test18_data = test18.model_dump()
        db_test18 = update_test18(db=db, id=id, test18_data=test18_data)
        return Test18Read.model_validate(db_test18)
    except Exception as e:
        logger.error(f"Error al actualizar Test18: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test18.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
