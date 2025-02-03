
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test19 import Test19Create, Test19Update, Test19Read
from db.models.test19 import Test19 as Test19Model
from db.crud.Maestro.Crud_test19 import create_test19, get_test19, gets_test19, delete_test19, update_test19
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test19",
    tags=["test19"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test19Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test19(test19: Test19Create, db: Session = Depends(get_db)):
    if test19.codigo is None or test19.descripcion is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test19_model = Test19Model(**test19.model_dump())
        db_test19 = create_test19(db=db, test19=test19_model)
        return Test19Read.model_validate(db_test19)
    except Exception as e:
        logger.error(f"Error al crear Test19: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{codigo}", response_model=Test19Read)
async def routes_get_test19_codigo(codigo: int, db: Session = Depends(get_db)):
    try:
        db_test19 = get_test19(db, codigo)
        if not db_test19:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test19 no encontrado")
        return Test19Read.model_validate(db_test19)
    except Exception as e:
        logger.error(f"Error al obtener Test19: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test19Read])
async def routes_gets_test19_all(db: Session = Depends(get_db)):
    try:
        db_test19 = gets_test19(db)
        if not db_test19:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test19s no encontrados")
        return [Test19Read.model_validate(test19) for test19 in db_test19]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test19: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{codigo}", response_model=Test19Read)
async def routes_delete_test19_numero(codigo: int, db: Session = Depends(get_db)):
    try:
        resultado_test19 = get_test19(db, codigo)
        if not resultado_test19:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test19 no encontrado")
        db_test19 = delete_test19(db, codigo)
        return Test19Read.model_validate(db_test19)
    except Exception as e:
        logger.error(f"Error al eliminar Test19: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{codigo}", response_model=Test19Read)
async def routes_update_test19(codigo: int, test19: Test19Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test19 con codigo = {codigo}")
    try:
        test19_data = test19.model_dump()
        db_test19 = update_test19(db=db, codigo=codigo, test19_data=test19_data)
        return Test19Read.model_validate(db_test19)
    except Exception as e:
        logger.error(f"Error al actualizar Test19: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test19.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
