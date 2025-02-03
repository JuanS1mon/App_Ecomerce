
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test8 import Test8Create, Test8Update, Test8Read
from db.models.test8 import Test8 as Test8Model
from db.crud.Maestro.Crud_test8 import create_test8, get_test8, gets_test8, delete_test8, update_test8
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test8",
    tags=["test8"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test8Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test8(test8: Test8Create, db: Session = Depends(get_db)):
    if test8.id is None or test8.nombre is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test8_model = Test8Model(**test8.model_dump())
        db_test8 = create_test8(db=db, test8=test8_model)
        return Test8Read.model_validate(db_test8)
    except Exception as e:
        logger.error(f"Error al crear Test8: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=Test8Read)
async def routes_get_test8_id(id: int, db: Session = Depends(get_db)):
    try:
        db_test8 = get_test8(db, id)
        if not db_test8:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test8 no encontrado")
        return Test8Read.model_validate(db_test8)
    except Exception as e:
        logger.error(f"Error al obtener Test8: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test8Read])
async def routes_gets_test8_all(db: Session = Depends(get_db)):
    try:
        db_test8 = gets_test8(db)
        if not db_test8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test8s no encontrados")
        return [Test8Read.model_validate(test8) for test8 in db_test8]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test8: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=Test8Read)
async def routes_delete_test8_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_test8 = get_test8(db, id)
        if not resultado_test8:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test8 no encontrado")
        db_test8 = delete_test8(db, id)
        return Test8Read.model_validate(db_test8)
    except Exception as e:
        logger.error(f"Error al eliminar Test8: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=Test8Read)
async def routes_update_test8(id: int, test8: Test8Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test8 con id = {id}")
    try:
        test8_data = test8.model_dump()
        db_test8 = update_test8(db=db, id=id, test8_data=test8_data)
        return Test8Read.model_validate(db_test8)
    except Exception as e:
        logger.error(f"Error al actualizar Test8: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test8.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
