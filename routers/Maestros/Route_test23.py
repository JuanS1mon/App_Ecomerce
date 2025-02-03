
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test23 import Test23Create, Test23Update, Test23Read
from db.models.test23 import Test23 as Test23Model
from db.crud.Maestro.Crud_test23 import create_test23, get_test23, gets_test23, delete_test23, update_test23
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test23",
    tags=["test23"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test23Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test23(test23: Test23Create, db: Session = Depends(get_db)):
    if test23.codigo is None or test23.descripcion is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test23_model = Test23Model(**test23.model_dump())
        db_test23 = create_test23(db=db, test23=test23_model)
        return Test23Read.model_validate(db_test23)
    except Exception as e:
        logger.error(f"Error al crear Test23: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{codigo}", response_model=Test23Read)
async def routes_get_test23_codigo(codigo: int, db: Session = Depends(get_db)):
    try:
        db_test23 = get_test23(db, codigo)
        if not db_test23:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test23 no encontrado")
        return Test23Read.model_validate(db_test23)
    except Exception as e:
        logger.error(f"Error al obtener Test23: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test23Read])
async def routes_gets_test23_all(db: Session = Depends(get_db)):
    try:
        db_test23 = gets_test23(db)
        if not db_test23:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test23s no encontrados")
        return [Test23Read.model_validate(test23) for test23 in db_test23]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test23: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{codigo}", response_model=Test23Read)
async def routes_delete_test23_numero(codigo: int, db: Session = Depends(get_db)):
    try:
        resultado_test23 = get_test23(db, codigo)
        if not resultado_test23:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test23 no encontrado")
        db_test23 = delete_test23(db, codigo)
        return Test23Read.model_validate(db_test23)
    except Exception as e:
        logger.error(f"Error al eliminar Test23: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{codigo}", response_model=Test23Read)
async def routes_update_test23(codigo: int, test23: Test23Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test23 con codigo = {codigo}")
    try:
        test23_data = test23.model_dump()
        db_test23 = update_test23(db=db, codigo=codigo, test23_data=test23_data)
        return Test23Read.model_validate(db_test23)
    except Exception as e:
        logger.error(f"Error al actualizar Test23: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test23.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
