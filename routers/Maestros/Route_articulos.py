
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_articulos import ArticulosCreate, ArticulosUpdate, ArticulosRead
from db.models.articulos import Articulos as ArticulosModel
from db.crud.Maestro.Crud_articulos import create_articulos, get_articulos, gets_articulos, delete_articulos, update_articulos
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/articulos",
    tags=["articulos"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=ArticulosRead, status_code=status.HTTP_201_CREATED)
async def routes_post_articulos(articulos: ArticulosCreate, db: Session = Depends(get_db)):
    if articulos.id is None or articulos.codigo is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        articulos_model = ArticulosModel(**articulos.model_dump())
        db_articulos = create_articulos(db=db, articulos=articulos_model)
        return ArticulosRead.model_validate(db_articulos)
    except Exception as e:
        logger.error(f"Error al crear Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=ArticulosRead)
async def routes_get_articulos_id(id: int, db: Session = Depends(get_db)):
    try:
        db_articulos = get_articulos(db, id)
        if not db_articulos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: articulos no encontrado")
        return ArticulosRead.model_validate(db_articulos)
    except Exception as e:
        logger.error(f"Error al obtener Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[ArticulosRead])
async def routes_gets_articulos_all(db: Session = Depends(get_db)):
    try:
        db_articulos = gets_articulos(db)
        if not db_articulos:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: articuloss no encontrados")
        return [ArticulosRead.model_validate(articulos) for articulos in db_articulos]
    except Exception as e:
        logger.error(f"Error al obtener registros de Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=ArticulosRead)
async def routes_delete_articulos_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_articulos = get_articulos(db, id)
        if not resultado_articulos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: articulos no encontrado")
        db_articulos = delete_articulos(db, id)
        return ArticulosRead.model_validate(db_articulos)
    except Exception as e:
        logger.error(f"Error al eliminar Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=ArticulosRead)
async def routes_update_articulos(id: int, articulos: ArticulosUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Articulos con id = {id}")
    try:
        articulos_data = articulos.model_dump()
        db_articulos = update_articulos(db=db, id=id, articulos_data=articulos_data)
        return ArticulosRead.model_validate(db_articulos)
    except Exception as e:
        logger.error(f"Error al actualizar Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/articulos.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
