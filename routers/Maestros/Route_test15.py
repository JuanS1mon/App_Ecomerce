
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test15 import Test15Create, Test15Update, Test15Read
from db.models.test15 import Test15 as Test15Model
from db.crud.Maestro.Crud_test15 import create_test15, get_test15, gets_test15, delete_test15, update_test15
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test15",
    tags=["test15"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test15Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test15(test15: Test15Create, db: Session = Depends(get_db)):
    if test15.co is None or test15.des is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test15_model = Test15Model(**test15.model_dump())
        db_test15 = create_test15(db=db, test15=test15_model)
        return Test15Read.model_validate(db_test15)
    except Exception as e:
        logger.error(f"Error al crear Test15: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{co}", response_model=Test15Read)
async def routes_get_test15_co(co: int, db: Session = Depends(get_db)):
    try:
        db_test15 = get_test15(db, co)
        if not db_test15:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test15 no encontrado")
        return Test15Read.model_validate(db_test15)
    except Exception as e:
        logger.error(f"Error al obtener Test15: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test15Read])
async def routes_gets_test15_all(db: Session = Depends(get_db)):
    try:
        db_test15 = gets_test15(db)
        if not db_test15:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test15s no encontrados")
        return [Test15Read.model_validate(test15) for test15 in db_test15]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test15: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{co}", response_model=Test15Read)
async def routes_delete_test15_numero(co: int, db: Session = Depends(get_db)):
    try:
        resultado_test15 = get_test15(db, co)
        if not resultado_test15:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test15 no encontrado")
        db_test15 = delete_test15(db, co)
        return Test15Read.model_validate(db_test15)
    except Exception as e:
        logger.error(f"Error al eliminar Test15: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{co}", response_model=Test15Read)
async def routes_update_test15(co: int, test15: Test15Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test15 con co = {co}")
    try:
        test15_data = test15.model_dump()
        db_test15 = update_test15(db=db, co=co, test15_data=test15_data)
        return Test15Read.model_validate(db_test15)
    except Exception as e:
        logger.error(f"Error al actualizar Test15: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test15.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
