from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from ....db.database import get_db
from .schema_articulos_series import Articulos_seriesCreate, Articulos_seriesUpdate, Articulos_seriesRead
from .model_articulos_series import Articulos_series as Articulos_seriesModel
from .service_articulos_series import create_articulos_series, get_articulos_series, gets_articulos_series, delete_articulos_series, update_articulos_series
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/articulos_series",
    tags=["articulos_series"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Articulos_seriesRead, status_code=status.HTTP_201_CREATED)
async def routes_post_articulos_series(articulos_series: Articulos_seriesCreate, db: Session = Depends(get_db)):
    # Verificar solo el campo obligatorio serie
    if articulos_series.serie is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="El campo serie es requerido")
    try:
        articulos_series_model = Articulos_seriesModel(**articulos_series.model_dump())
        db_articulos_series = create_articulos_series(db=db, articulos_series=articulos_series_model)
        return Articulos_seriesRead.model_validate(db_articulos_series)
    except Exception as e:
        logger.error(f"Error al crear Articulos_series: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=Articulos_seriesRead)
async def routes_get_articulos_series_id(id: int, db: Session = Depends(get_db)):
    try:
        db_articulos_series = get_articulos_series(db, id)
        if not db_articulos_series:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: articulos_series no encontrado")
        return Articulos_seriesRead.model_validate(db_articulos_series)
    except Exception as e:
        logger.error(f"Error al obtener Articulos_series: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Articulos_seriesRead])
async def routes_gets_articulos_series_all(db: Session = Depends(get_db)):
    try:
        db_articulos_series = gets_articulos_series(db)
        # Eliminamos la validación que provocaba el error 400
        # Si no hay registros, simplemente devolvemos una lista vacía
        return [Articulos_seriesRead.model_validate(articulos_series) for articulos_series in db_articulos_series]
    except Exception as e:
        logger.error(f"Error al obtener registros de Articulos_series: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=Articulos_seriesRead)
async def routes_delete_articulos_series_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_articulos_series = get_articulos_series(db, id)
        if not resultado_articulos_series:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: articulos_series no encontrado")
        db_articulos_series = delete_articulos_series(db, id)
        return Articulos_seriesRead.model_validate(db_articulos_series)
    except Exception as e:
        logger.error(f"Error al eliminar Articulos_series: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=Articulos_seriesRead)
async def routes_update_articulos_series(id: int, articulos_series: Articulos_seriesUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Articulos_series con id = {id}")
    try:
        articulos_series_data = articulos_series.model_dump()
        db_articulos_series = update_articulos_series(db=db, id=id, articulos_series_data=articulos_series_data)
        return Articulos_seriesRead.model_validate(db_articulos_series)
    except Exception as e:
        logger.error(f"Error al actualizar Articulos_series: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Ruta actualizada: ahora buscamos en static/module_name/index.html
        with open(f"sql_app/static/app_stock/articulos_series/articulos_serie.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
