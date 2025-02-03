
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test9 import Test9Create, Test9Update, Test9Read
from db.models.test9 import Test9 as Test9Model
from db.crud.Maestro.Crud_test9 import create_test9, get_test9, gets_test9, delete_test9, update_test9
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test9",
    tags=["test9"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test9Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test9(test9: Test9Create, db: Session = Depends(get_db)):
    if test9.id is None or test9.nombre is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test9_model = Test9Model(**test9.model_dump())
        db_test9 = create_test9(db=db, test9=test9_model)
        return Test9Read.model_validate(db_test9)
    except Exception as e:
        logger.error(f"Error al crear Test9: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=Test9Read)
async def routes_get_test9_id(id: int, db: Session = Depends(get_db)):
    try:
        db_test9 = get_test9(db, id)
        if not db_test9:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test9 no encontrado")
        return Test9Read.model_validate(db_test9)
    except Exception as e:
        logger.error(f"Error al obtener Test9: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test9Read])
async def routes_gets_test9_all(db: Session = Depends(get_db)):
    try:
        db_test9 = gets_test9(db)
        if not db_test9:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test9s no encontrados")
        return [Test9Read.model_validate(test9) for test9 in db_test9]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test9: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=Test9Read)
async def routes_delete_test9_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_test9 = get_test9(db, id)
        if not resultado_test9:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test9 no encontrado")
        db_test9 = delete_test9(db, id)
        return Test9Read.model_validate(db_test9)
    except Exception as e:
        logger.error(f"Error al eliminar Test9: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=Test9Read)
async def routes_update_test9(id: int, test9: Test9Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test9 con id = {id}")
    try:
        test9_data = test9.model_dump()
        db_test9 = update_test9(db=db, id=id, test9_data=test9_data)
        return Test9Read.model_validate(db_test9)
    except Exception as e:
        logger.error(f"Error al actualizar Test9: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test9.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
