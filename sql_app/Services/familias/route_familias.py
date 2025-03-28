
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_familias import FamiliasCreate, FamiliasUpdate, FamiliasRead
from db.models.familias import Familias as FamiliasModel
from db.crud.Maestro.Crud_familias import create_familias, get_familias, gets_familias, delete_familias, update_familias
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/familias",
    tags=["familias"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=FamiliasRead, status_code=status.HTTP_201_CREATED)
async def routes_post_familias(familias: FamiliasCreate, db: Session = Depends(get_db)):
    if familias.tetwe is None or familias.asd is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        familias_model = FamiliasModel(**familias.model_dump())
        db_familias = create_familias(db=db, familias=familias_model)
        return FamiliasRead.model_validate(db_familias)
    except Exception as e:
        logger.error(f"Error al crear Familias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{tetwe}", response_model=FamiliasRead)
async def routes_get_familias_tetwe(tetwe: int, db: Session = Depends(get_db)):
    try:
        db_familias = get_familias(db, tetwe)
        if not db_familias:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: familias no encontrado")
        return FamiliasRead.model_validate(db_familias)
    except Exception as e:
        logger.error(f"Error al obtener Familias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[FamiliasRead])
async def routes_gets_familias_all(db: Session = Depends(get_db)):
    try:
        db_familias = gets_familias(db)
        if not db_familias:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: familiass no encontrados")
        return [FamiliasRead.model_validate(familias) for familias in db_familias]
    except Exception as e:
        logger.error(f"Error al obtener registros de Familias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{tetwe}", response_model=FamiliasRead)
async def routes_delete_familias_numero(tetwe: int, db: Session = Depends(get_db)):
    try:
        resultado_familias = get_familias(db, tetwe)
        if not resultado_familias:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: familias no encontrado")
        db_familias = delete_familias(db, tetwe)
        return FamiliasRead.model_validate(db_familias)
    except Exception as e:
        logger.error(f"Error al eliminar Familias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{tetwe}", response_model=FamiliasRead)
async def routes_update_familias(tetwe: int, familias: FamiliasUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Familias con tetwe = {tetwe}")
    try:
        familias_data = familias.model_dump()
        db_familias = update_familias(db=db, tetwe=tetwe, familias_data=familias_data)
        return FamiliasRead.model_validate(db_familias)
    except Exception as e:
        logger.error(f"Error al actualizar Familias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/familias.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
