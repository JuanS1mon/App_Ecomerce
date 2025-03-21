
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_planilla_test import Planilla_testCreate, Planilla_testUpdate, Planilla_testRead
from db.models.planilla_test import Planilla_test as Planilla_testModel
from db.crud.Maestro.Crud_planilla_test import create_planilla_test, get_planilla_test, gets_planilla_test, delete_planilla_test, update_planilla_test
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/planilla_test",
    tags=["planilla_test"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Planilla_testRead, status_code=status.HTTP_201_CREATED)
async def routes_post_planilla_test(planilla_test: Planilla_testCreate, db: Session = Depends(get_db)):
    if planilla_test.codigo is None or planilla_test.fecha is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        planilla_test_model = Planilla_testModel(**planilla_test.model_dump())
        db_planilla_test = create_planilla_test(db=db, planilla_test=planilla_test_model)
        return Planilla_testRead.model_validate(db_planilla_test)
    except Exception as e:
        logger.error(f"Error al crear Planilla_test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{codigo}", response_model=Planilla_testRead)
async def routes_get_planilla_test_codigo(codigo: int, db: Session = Depends(get_db)):
    try:
        db_planilla_test = get_planilla_test(db, codigo)
        if not db_planilla_test:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: planilla_test no encontrado")
        return Planilla_testRead.model_validate(db_planilla_test)
    except Exception as e:
        logger.error(f"Error al obtener Planilla_test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Planilla_testRead])
async def routes_gets_planilla_test_all(db: Session = Depends(get_db)):
    try:
        db_planilla_test = gets_planilla_test(db)
        if not db_planilla_test:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: planilla_tests no encontrados")
        return [Planilla_testRead.model_validate(planilla_test) for planilla_test in db_planilla_test]
    except Exception as e:
        logger.error(f"Error al obtener registros de Planilla_test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{codigo}", response_model=Planilla_testRead)
async def routes_delete_planilla_test_numero(codigo: int, db: Session = Depends(get_db)):
    try:
        resultado_planilla_test = get_planilla_test(db, codigo)
        if not resultado_planilla_test:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: planilla_test no encontrado")
        db_planilla_test = delete_planilla_test(db, codigo)
        return Planilla_testRead.model_validate(db_planilla_test)
    except Exception as e:
        logger.error(f"Error al eliminar Planilla_test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{codigo}", response_model=Planilla_testRead)
async def routes_update_planilla_test(codigo: int, planilla_test: Planilla_testUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Planilla_test con codigo = {codigo}")
    try:
        planilla_test_data = planilla_test.model_dump()
        db_planilla_test = update_planilla_test(db=db, codigo=codigo, planilla_test_data=planilla_test_data)
        return Planilla_testRead.model_validate(db_planilla_test)
    except Exception as e:
        logger.error(f"Error al actualizar Planilla_test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/planilla_test.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
