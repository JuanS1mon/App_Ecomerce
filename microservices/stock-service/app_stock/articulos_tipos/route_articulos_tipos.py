
# Imports de bibliotecas estándar
import logging
from typing import List, Optional

# Imports de terceros
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

# Imports del proyecto
from db.database import get_db
from Services.app_stock.articulos_tipos.model_articulos_tipos import Articulos_tipos as Articulos_tiposModel
from Services.app_stock.articulos_tipos.schema_articulos_tipos import Articulos_tiposCreate, Articulos_tiposRead, Articulos_tiposUpdate
from Services.app_stock.articulos_tipos.service_articulos_tipos import (
    create_articulos_tipos,
    delete_articulos_tipos,
    get_articulos_tipos,
    gets_articulos_tipos,
    update_articulos_tipos
)

from db.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/articulos_tipos",
    tags=["articulos_tipos"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Articulos_tiposRead, status_code=status.HTTP_201_CREATED)
async def routes_post_articulos_tipos(articulos_tipos: Articulos_tiposCreate, db: Session = Depends(get_db)):
    if articulos_tipos.descripcion is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="El campo descripción es obligatorio")
    try:
        articulos_tipos_model = Articulos_tiposModel(**articulos_tipos.model_dump())
        db_articulos_tipos = create_articulos_tipos(db=db, articulos_tipos=articulos_tipos_model)
        return Articulos_tiposRead.model_validate(db_articulos_tipos)
    except Exception as e:
        logger.error(f"Error al crear Articulos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=Articulos_tiposRead)
async def routes_get_articulos_tipos_id(id: int, db: Session = Depends(get_db)):
    try:
        db_articulos_tipos = get_articulos_tipos(db, id)
        if not db_articulos_tipos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: articulos_tipos no encontrado")
        return Articulos_tiposRead.model_validate(db_articulos_tipos)
    except Exception as e:
        logger.error(f"Error al obtener Articulos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Articulos_tiposRead])
async def routes_gets_articulos_tipos_all(db: Session = Depends(get_db)):
    try:
        db_articulos_tipos = gets_articulos_tipos(db)
        if not db_articulos_tipos:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: articulos_tiposs no encontrados")
        return [Articulos_tiposRead.model_validate(articulos_tipos) for articulos_tipos in db_articulos_tipos]
    except Exception as e:
        logger.error(f"Error al obtener registros de Articulos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=Articulos_tiposRead)
async def routes_delete_articulos_tipos_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_articulos_tipos = get_articulos_tipos(db, id)
        if not resultado_articulos_tipos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: articulos_tipos no encontrado")
        db_articulos_tipos = delete_articulos_tipos(db, id)
        return Articulos_tiposRead.model_validate(db_articulos_tipos)
    except Exception as e:
        logger.error(f"Error al eliminar Articulos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=Articulos_tiposRead)
async def routes_update_articulos_tipos(id: int, articulos_tipos: Articulos_tiposUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Articulos_tipos con id = {id}")
    try:
        articulos_tipos_data = articulos_tipos.model_dump()
        db_articulos_tipos = update_articulos_tipos(db=db, id=id, articulos_tipos_data=articulos_tipos_data)
        return Articulos_tiposRead.model_validate(db_articulos_tipos)
    except Exception as e:
        logger.error(f"Error al actualizar Articulos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Ruta actualizada: ahora buscamos en static/module_name/index.html
        with open(f"sql_app/static/app_stock/articulos_tipos/articulos_tipos.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
