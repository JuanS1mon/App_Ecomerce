
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test6 import Test6Create, Test6Update, Test6Read
from db.models.test6 import Test6 as Test6Model
from db.crud.Maestro.Crud_test6 import create_test6, get_test6, gets_test6, delete_test6, update_test6
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test6",
    tags=["test6"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test6Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test6(test6: Test6Create, db: Session = Depends(get_db)):
    if test6.codigo_int is None or test6.nombre is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test6_model = Test6Model(**test6.model_dump())
        db_test6 = create_test6(db=db, test6=test6_model)
        return Test6Read.model_validate(db_test6)
    except Exception as e:
        logger.error(f"Error al crear Test6: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{codigo_int}", response_model=Test6Read)
async def routes_get_test6_codigo_int(codigo_int: int, db: Session = Depends(get_db)):
    try:
        db_test6 = get_test6(db, codigo_int)
        if not db_test6:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test6 no encontrado")
        return Test6Read.model_validate(db_test6)
    except Exception as e:
        logger.error(f"Error al obtener Test6: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test6Read])
async def routes_gets_test6_all(db: Session = Depends(get_db)):
    try:
        db_test6 = gets_test6(db)
        if not db_test6:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test6s no encontrados")
        return [Test6Read.model_validate(test6) for test6 in db_test6]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test6: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{codigo_int}", response_model=Test6Read)
async def routes_delete_test6_numero(codigo_int: int, db: Session = Depends(get_db)):
    try:
        resultado_test6 = get_test6(db, codigo_int)
        if not resultado_test6:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test6 no encontrado")
        db_test6 = delete_test6(db, codigo_int)
        return Test6Read.model_validate(db_test6)
    except Exception as e:
        logger.error(f"Error al eliminar Test6: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{codigo_int}", response_model=Test6Read)
async def routes_update_test6(codigo_int: int, test6: Test6Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test6 con codigo_int = {codigo_int}")
    try:
        test6_data = test6.model_dump()
        db_test6 = update_test6(db=db, codigo_int=codigo_int, test6_data=test6_data)
        return Test6Read.model_validate(db_test6)
    except Exception as e:
        logger.error(f"Error al actualizar Test6: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test6.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
