
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test5 import Test5Create, Test5Update, Test5Read
from db.models.test5 import Test5 as Test5Model
from db.crud.Maestro.Crud_test5 import create_test5, get_test5, gets_test5, delete_test5, update_test5
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test5",
    tags=["test5"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test5Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test5(test5: Test5Create, db: Session = Depends(get_db)):
    if test5.codigo is None or test5.nombre is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test5_model = Test5Model(**test5.model_dump())
        db_test5 = create_test5(db=db, test5=test5_model)
        return Test5Read.model_validate(db_test5)
    except Exception as e:
        logger.error(f"Error al crear Test5: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{codigo}", response_model=Test5Read)
async def routes_get_test5_codigo(codigo: int, db: Session = Depends(get_db)):
    try:
        db_test5 = get_test5(db, codigo)
        if not db_test5:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test5 no encontrado")
        return Test5Read.model_validate(db_test5)
    except Exception as e:
        logger.error(f"Error al obtener Test5: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test5Read])
async def routes_gets_test5_all(db: Session = Depends(get_db)):
    try:
        db_test5 = gets_test5(db)
        if not db_test5:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test5s no encontrados")
        return [Test5Read.model_validate(test5) for test5 in db_test5]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test5: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{codigo}", response_model=Test5Read)
async def routes_delete_test5_numero(codigo: int, db: Session = Depends(get_db)):
    try:
        resultado_test5 = get_test5(db, codigo)
        if not resultado_test5:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test5 no encontrado")
        db_test5 = delete_test5(db, codigo)
        return Test5Read.model_validate(db_test5)
    except Exception as e:
        logger.error(f"Error al eliminar Test5: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{codigo}", response_model=Test5Read)
async def routes_update_test5(codigo: int, test5: Test5Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test5 con codigo = {codigo}")
    try:
        test5_data = test5.model_dump()
        db_test5 = update_test5(db=db, codigo=codigo, test5_data=test5_data)
        return Test5Read.model_validate(db_test5)
    except Exception as e:
        logger.error(f"Error al actualizar Test5: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test5.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
