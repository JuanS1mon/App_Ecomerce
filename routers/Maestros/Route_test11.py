
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test11 import Test11Create, Test11Update, Test11Read
from db.models.test11 import Test11 as Test11Model
from db.crud.Maestro.Crud_test11 import create_test11, get_test11, gets_test11, delete_test11, update_test11
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test11",
    tags=["test11"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test11Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test11(test11: Test11Create, db: Session = Depends(get_db)):
    if test11.codigo is None or test11.nombre is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test11_model = Test11Model(**test11.model_dump())
        db_test11 = create_test11(db=db, test11=test11_model)
        return Test11Read.model_validate(db_test11)
    except Exception as e:
        logger.error(f"Error al crear Test11: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{codigo}", response_model=Test11Read)
async def routes_get_test11_codigo(codigo: int, db: Session = Depends(get_db)):
    try:
        db_test11 = get_test11(db, codigo)
        if not db_test11:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test11 no encontrado")
        return Test11Read.model_validate(db_test11)
    except Exception as e:
        logger.error(f"Error al obtener Test11: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test11Read])
async def routes_gets_test11_all(db: Session = Depends(get_db)):
    try:
        db_test11 = gets_test11(db)
        if not db_test11:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test11s no encontrados")
        return [Test11Read.model_validate(test11) for test11 in db_test11]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test11: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{codigo}", response_model=Test11Read)
async def routes_delete_test11_numero(codigo: int, db: Session = Depends(get_db)):
    try:
        resultado_test11 = get_test11(db, codigo)
        if not resultado_test11:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test11 no encontrado")
        db_test11 = delete_test11(db, codigo)
        return Test11Read.model_validate(db_test11)
    except Exception as e:
        logger.error(f"Error al eliminar Test11: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{codigo}", response_model=Test11Read)
async def routes_update_test11(codigo: int, test11: Test11Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test11 con codigo = {codigo}")
    try:
        test11_data = test11.model_dump()
        db_test11 = update_test11(db=db, codigo=codigo, test11_data=test11_data)
        return Test11Read.model_validate(db_test11)
    except Exception as e:
        logger.error(f"Error al actualizar Test11: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test11.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
