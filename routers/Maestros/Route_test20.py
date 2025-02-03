
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test20 import Test20Create, Test20Update, Test20Read
from db.models.test20 import Test20 as Test20Model
from db.crud.Maestro.Crud_test20 import create_test20, get_test20, gets_test20, delete_test20, update_test20
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test20",
    tags=["test20"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test20Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test20(test20: Test20Create, db: Session = Depends(get_db)):
    if test20.codigo is None or test20.descripcion is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test20_model = Test20Model(**test20.model_dump())
        db_test20 = create_test20(db=db, test20=test20_model)
        return Test20Read.model_validate(db_test20)
    except Exception as e:
        logger.error(f"Error al crear Test20: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{codigo}", response_model=Test20Read)
async def routes_get_test20_codigo(codigo: int, db: Session = Depends(get_db)):
    try:
        db_test20 = get_test20(db, codigo)
        if not db_test20:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test20 no encontrado")
        return Test20Read.model_validate(db_test20)
    except Exception as e:
        logger.error(f"Error al obtener Test20: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test20Read])
async def routes_gets_test20_all(db: Session = Depends(get_db)):
    try:
        db_test20 = gets_test20(db)
        if not db_test20:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test20s no encontrados")
        return [Test20Read.model_validate(test20) for test20 in db_test20]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test20: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{codigo}", response_model=Test20Read)
async def routes_delete_test20_numero(codigo: int, db: Session = Depends(get_db)):
    try:
        resultado_test20 = get_test20(db, codigo)
        if not resultado_test20:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test20 no encontrado")
        db_test20 = delete_test20(db, codigo)
        return Test20Read.model_validate(db_test20)
    except Exception as e:
        logger.error(f"Error al eliminar Test20: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{codigo}", response_model=Test20Read)
async def routes_update_test20(codigo: int, test20: Test20Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test20 con codigo = {codigo}")
    try:
        test20_data = test20.model_dump()
        db_test20 = update_test20(db=db, codigo=codigo, test20_data=test20_data)
        return Test20Read.model_validate(db_test20)
    except Exception as e:
        logger.error(f"Error al actualizar Test20: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test20.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
