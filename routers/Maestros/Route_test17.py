
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test17 import Test17Create, Test17Update, Test17Read
from db.models.test17 import Test17 as Test17Model
from db.crud.Maestro.Crud_test17 import create_test17, get_test17, gets_test17, delete_test17, update_test17
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test17",
    tags=["test17"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test17Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test17(test17: Test17Create, db: Session = Depends(get_db)):
    if test17.cod is None or test17.desc is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test17_model = Test17Model(**test17.model_dump())
        db_test17 = create_test17(db=db, test17=test17_model)
        return Test17Read.model_validate(db_test17)
    except Exception as e:
        logger.error(f"Error al crear Test17: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{cod}", response_model=Test17Read)
async def routes_get_test17_cod(cod: int, db: Session = Depends(get_db)):
    try:
        db_test17 = get_test17(db, cod)
        if not db_test17:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test17 no encontrado")
        return Test17Read.model_validate(db_test17)
    except Exception as e:
        logger.error(f"Error al obtener Test17: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test17Read])
async def routes_gets_test17_all(db: Session = Depends(get_db)):
    try:
        db_test17 = gets_test17(db)
        if not db_test17:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test17s no encontrados")
        return [Test17Read.model_validate(test17) for test17 in db_test17]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test17: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{cod}", response_model=Test17Read)
async def routes_delete_test17_numero(cod: int, db: Session = Depends(get_db)):
    try:
        resultado_test17 = get_test17(db, cod)
        if not resultado_test17:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test17 no encontrado")
        db_test17 = delete_test17(db, cod)
        return Test17Read.model_validate(db_test17)
    except Exception as e:
        logger.error(f"Error al eliminar Test17: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{cod}", response_model=Test17Read)
async def routes_update_test17(cod: int, test17: Test17Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test17 con cod = {cod}")
    try:
        test17_data = test17.model_dump()
        db_test17 = update_test17(db=db, cod=cod, test17_data=test17_data)
        return Test17Read.model_validate(db_test17)
    except Exception as e:
        logger.error(f"Error al actualizar Test17: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test17.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
