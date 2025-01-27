
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test4 import Test4Create, Test4Update, Test4Read
from db.models.test4 import Test4 as Test4Model
from db.crud.Maestro.Crud_test4 import create_test4, get_test4, gets_test4, delete_test4, update_test4
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test4",
    tags=["test4"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test4Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test4(test4: Test4Create, db: Session = Depends(get_db)):
    if test4.codigo is None or test4.nombre is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test4_model = Test4Model(**test4.model_dump())
        db_test4 = create_test4(db=db, test4=test4_model)
        return Test4Read.model_validate(db_test4)
    except Exception as e:
        logger.error(f"Error al crear Test4: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{codigo}", response_model=Test4Read)
async def routes_get_test4_codigo(codigo: int, db: Session = Depends(get_db)):
    try:
        db_test4 = get_test4(db, codigo)
        if not db_test4:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test4 no encontrado")
        return Test4Read.model_validate(db_test4)
    except Exception as e:
        logger.error(f"Error al obtener Test4: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test4Read])
async def routes_gets_test4_all(db: Session = Depends(get_db)):
    try:
        db_test4 = gets_test4(db)
        if not db_test4:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test4s no encontrados")
        return [Test4Read.model_validate(test4) for test4 in db_test4]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test4: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{codigo}", response_model=Test4Read)
async def routes_delete_test4_numero(codigo: int, db: Session = Depends(get_db)):
    try:
        resultado_test4 = get_test4(db, codigo)
        if not resultado_test4:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test4 no encontrado")
        db_test4 = delete_test4(db, codigo)
        return Test4Read.model_validate(db_test4)
    except Exception as e:
        logger.error(f"Error al eliminar Test4: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{codigo}", response_model=Test4Read)
async def routes_update_test4(codigo: int, test4: Test4Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test4 con codigo = {codigo}")
    try:
        test4_data = test4.model_dump()
        db_test4 = update_test4(db=db, codigo=codigo, test4_data=test4_data)
        return Test4Read.model_validate(db_test4)
    except Exception as e:
        logger.error(f"Error al actualizar Test4: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test4.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
