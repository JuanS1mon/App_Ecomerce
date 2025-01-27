
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test2 import Test2Create, Test2Update, Test2Read
from db.models.test2 import Test2 as Test2Model
from db.crud.Maestro.Crud_test2 import create_test2, get_test2, gets_test2, delete_test2, update_test2
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test2",
    tags=["test2"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test2Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test2(test2: Test2Create, db: Session = Depends(get_db)):
    if test2.codigo is None or test2.nombre is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test2_model = Test2Model(**test2.model_dump())
        db_test2 = create_test2(db=db, test2=test2_model)
        return Test2Read.model_validate(db_test2)
    except Exception as e:
        logger.error(f"Error al crear Test2: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{codigo}", response_model=Test2Read)
async def routes_get_test2_codigo(codigo: int, db: Session = Depends(get_db)):
    try:
        db_test2 = get_test2(db, codigo)
        if not db_test2:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test2 no encontrado")
        return Test2Read.model_validate(db_test2)
    except Exception as e:
        logger.error(f"Error al obtener Test2: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test2Read])
async def routes_gets_test2_all(db: Session = Depends(get_db)):
    try:
        db_test2 = gets_test2(db)
        if not db_test2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test2s no encontrados")
        return [Test2Read.model_validate(test2) for test2 in db_test2]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test2: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{codigo}", response_model=Test2Read)
async def routes_delete_test2_numero(codigo: int, db: Session = Depends(get_db)):
    try:
        resultado_test2 = get_test2(db, codigo)
        if not resultado_test2:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test2 no encontrado")
        db_test2 = delete_test2(db, codigo)
        return Test2Read.model_validate(db_test2)
    except Exception as e:
        logger.error(f"Error al eliminar Test2: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{codigo}", response_model=Test2Read)
async def routes_update_test2(codigo: int, test2: Test2Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test2 con codigo = {codigo}")
    try:
        test2_data = test2.model_dump()
        db_test2 = update_test2(db=db, codigo=codigo, test2_data=test2_data)
        return Test2Read.model_validate(db_test2)
    except Exception as e:
        logger.error(f"Error al actualizar Test2: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test2.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
