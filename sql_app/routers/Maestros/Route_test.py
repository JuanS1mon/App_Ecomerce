
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test import TestCreate, TestUpdate, TestRead
from db.models.test import Test as TestModel
from db.crud.Maestro.Crud_test import create_test, get_test, gets_test, delete_test, update_test
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test",
    tags=["test"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=TestRead, status_code=status.HTTP_201_CREATED)
async def routes_post_test(test: TestCreate, db: Session = Depends(get_db)):
    if test.id is None or test.campo1 is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test_model = TestModel(**test.model_dump())
        db_test = create_test(db=db, test=test_model)
        return TestRead.model_validate(db_test)
    except Exception as e:
        logger.error(f"Error al crear Test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=TestRead)
async def routes_get_test_id(id: int, db: Session = Depends(get_db)):
    try:
        db_test = get_test(db, id)
        if not db_test:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test no encontrado")
        return TestRead.model_validate(db_test)
    except Exception as e:
        logger.error(f"Error al obtener Test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[TestRead])
async def routes_gets_test_all(db: Session = Depends(get_db)):
    try:
        db_test = gets_test(db)
        if not db_test:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: tests no encontrados")
        return [TestRead.model_validate(test) for test in db_test]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=TestRead)
async def routes_delete_test_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_test = get_test(db, id)
        if not resultado_test:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test no encontrado")
        db_test = delete_test(db, id)
        return TestRead.model_validate(db_test)
    except Exception as e:
        logger.error(f"Error al eliminar Test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=TestRead)
async def routes_update_test(id: int, test: TestUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test con id = {id}")
    try:
        test_data = test.model_dump()
        db_test = update_test(db=db, id=id, test_data=test_data)
        return TestRead.model_validate(db_test)
    except Exception as e:
        logger.error(f"Error al actualizar Test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
