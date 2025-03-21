
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_rubros import RubrosCreate, RubrosUpdate, RubrosRead
from db.models.rubros import Rubros as RubrosModel
from db.crud.Maestro.Crud_rubros import create_rubros, get_rubros, gets_rubros, delete_rubros, update_rubros
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/rubros",
    tags=["rubros"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=RubrosRead, status_code=status.HTTP_201_CREATED)
async def routes_post_rubros(rubros: RubrosCreate, db: Session = Depends(get_db)):
    if rubros.codigo is None or rubros.test1 is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        rubros_model = RubrosModel(**rubros.model_dump())
        db_rubros = create_rubros(db=db, rubros=rubros_model)
        return RubrosRead.model_validate(db_rubros)
    except Exception as e:
        logger.error(f"Error al crear Rubros: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{codigo}", response_model=RubrosRead)
async def routes_get_rubros_codigo(codigo: int, db: Session = Depends(get_db)):
    try:
        db_rubros = get_rubros(db, codigo)
        if not db_rubros:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: rubros no encontrado")
        return RubrosRead.model_validate(db_rubros)
    except Exception as e:
        logger.error(f"Error al obtener Rubros: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[RubrosRead])
async def routes_gets_rubros_all(db: Session = Depends(get_db)):
    try:
        db_rubros = gets_rubros(db)
        if not db_rubros:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: rubross no encontrados")
        return [RubrosRead.model_validate(rubros) for rubros in db_rubros]
    except Exception as e:
        logger.error(f"Error al obtener registros de Rubros: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{codigo}", response_model=RubrosRead)
async def routes_delete_rubros_numero(codigo: int, db: Session = Depends(get_db)):
    try:
        resultado_rubros = get_rubros(db, codigo)
        if not resultado_rubros:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: rubros no encontrado")
        db_rubros = delete_rubros(db, codigo)
        return RubrosRead.model_validate(db_rubros)
    except Exception as e:
        logger.error(f"Error al eliminar Rubros: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{codigo}", response_model=RubrosRead)
async def routes_update_rubros(codigo: int, rubros: RubrosUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Rubros con codigo = {codigo}")
    try:
        rubros_data = rubros.model_dump()
        db_rubros = update_rubros(db=db, codigo=codigo, rubros_data=rubros_data)
        return RubrosRead.model_validate(db_rubros)
    except Exception as e:
        logger.error(f"Error al actualizar Rubros: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/rubros.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
