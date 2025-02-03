
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test7 import Test7Create, Test7Update, Test7Read
from db.models.test7 import Test7 as Test7Model
from db.crud.Maestro.Crud_test7 import create_test7, get_test7, gets_test7, delete_test7, update_test7
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test7",
    tags=["test7"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test7Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test7(test7: Test7Create, db: Session = Depends(get_db)):
    if test7.id is None or test7.nombre is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test7_model = Test7Model(**test7.model_dump())
        db_test7 = create_test7(db=db, test7=test7_model)
        return Test7Read.model_validate(db_test7)
    except Exception as e:
        logger.error(f"Error al crear Test7: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=Test7Read)
async def routes_get_test7_id(id: int, db: Session = Depends(get_db)):
    try:
        db_test7 = get_test7(db, id)
        if not db_test7:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test7 no encontrado")
        return Test7Read.model_validate(db_test7)
    except Exception as e:
        logger.error(f"Error al obtener Test7: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test7Read])
async def routes_gets_test7_all(db: Session = Depends(get_db)):
    try:
        db_test7 = gets_test7(db)
        if not db_test7:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test7s no encontrados")
        return [Test7Read.model_validate(test7) for test7 in db_test7]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test7: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=Test7Read)
async def routes_delete_test7_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_test7 = get_test7(db, id)
        if not resultado_test7:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test7 no encontrado")
        db_test7 = delete_test7(db, id)
        return Test7Read.model_validate(db_test7)
    except Exception as e:
        logger.error(f"Error al eliminar Test7: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=Test7Read)
async def routes_update_test7(id: int, test7: Test7Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test7 con id = {id}")
    try:
        test7_data = test7.model_dump()
        db_test7 = update_test7(db=db, id=id, test7_data=test7_data)
        return Test7Read.model_validate(db_test7)
    except Exception as e:
        logger.error(f"Error al actualizar Test7: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test7.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
