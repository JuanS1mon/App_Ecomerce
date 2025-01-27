
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test3 import Test3Create, Test3Update, Test3Read
from db.models.test3 import Test3 as Test3Model
from db.crud.Maestro.Crud_test3 import create_test3, get_test3, gets_test3, delete_test3, update_test3
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test3",
    tags=["test3"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test3Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test3(test3: Test3Create, db: Session = Depends(get_db)):
    if test3.codigo is None or test3.fecha is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test3_model = Test3Model(**test3.model_dump())
        db_test3 = create_test3(db=db, test3=test3_model)
        return Test3Read.model_validate(db_test3)
    except Exception as e:
        logger.error(f"Error al crear Test3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{codigo}", response_model=Test3Read)
async def routes_get_test3_codigo(codigo: int, db: Session = Depends(get_db)):
    try:
        db_test3 = get_test3(db, codigo)
        if not db_test3:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test3 no encontrado")
        return Test3Read.model_validate(db_test3)
    except Exception as e:
        logger.error(f"Error al obtener Test3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test3Read])
async def routes_gets_test3_all(db: Session = Depends(get_db)):
    try:
        db_test3 = gets_test3(db)
        if not db_test3:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test3s no encontrados")
        return [Test3Read.model_validate(test3) for test3 in db_test3]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{codigo}", response_model=Test3Read)
async def routes_delete_test3_numero(codigo: int, db: Session = Depends(get_db)):
    try:
        resultado_test3 = get_test3(db, codigo)
        if not resultado_test3:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test3 no encontrado")
        db_test3 = delete_test3(db, codigo)
        return Test3Read.model_validate(db_test3)
    except Exception as e:
        logger.error(f"Error al eliminar Test3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{codigo}", response_model=Test3Read)
async def routes_update_test3(codigo: int, test3: Test3Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test3 con codigo = {codigo}")
    try:
        test3_data = test3.model_dump()
        db_test3 = update_test3(db=db, codigo=codigo, test3_data=test3_data)
        return Test3Read.model_validate(db_test3)
    except Exception as e:
        logger.error(f"Error al actualizar Test3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test3.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
