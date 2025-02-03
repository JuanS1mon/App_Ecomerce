
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_test22 import Test22Create, Test22Update, Test22Read
from db.models.test22 import Test22 as Test22Model
from db.crud.Maestro.Crud_test22 import create_test22, get_test22, gets_test22, delete_test22, update_test22
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/test22",
    tags=["test22"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Test22Read, status_code=status.HTTP_201_CREATED)
async def routes_post_test22(test22: Test22Create, db: Session = Depends(get_db)):
    if test22.codigo is None or test22.descripcion is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        test22_model = Test22Model(**test22.model_dump())
        db_test22 = create_test22(db=db, test22=test22_model)
        return Test22Read.model_validate(db_test22)
    except Exception as e:
        logger.error(f"Error al crear Test22: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{codigo}", response_model=Test22Read)
async def routes_get_test22_codigo(codigo: int, db: Session = Depends(get_db)):
    try:
        db_test22 = get_test22(db, codigo)
        if not db_test22:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test22 no encontrado")
        return Test22Read.model_validate(db_test22)
    except Exception as e:
        logger.error(f"Error al obtener Test22: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Test22Read])
async def routes_gets_test22_all(db: Session = Depends(get_db)):
    try:
        db_test22 = gets_test22(db)
        if not db_test22:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: test22s no encontrados")
        return [Test22Read.model_validate(test22) for test22 in db_test22]
    except Exception as e:
        logger.error(f"Error al obtener registros de Test22: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{codigo}", response_model=Test22Read)
async def routes_delete_test22_numero(codigo: int, db: Session = Depends(get_db)):
    try:
        resultado_test22 = get_test22(db, codigo)
        if not resultado_test22:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: test22 no encontrado")
        db_test22 = delete_test22(db, codigo)
        return Test22Read.model_validate(db_test22)
    except Exception as e:
        logger.error(f"Error al eliminar Test22: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{codigo}", response_model=Test22Read)
async def routes_update_test22(codigo: int, test22: Test22Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Test22 con codigo = {codigo}")
    try:
        test22_data = test22.model_dump()
        db_test22 = update_test22(db=db, codigo=codigo, test22_data=test22_data)
        return Test22Read.model_validate(db_test22)
    except Exception as e:
        logger.error(f"Error al actualizar Test22: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/test22.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
