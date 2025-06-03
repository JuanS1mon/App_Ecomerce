from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from .schema_depositos_tipos import Depositos_tiposCreate, Depositos_tiposUpdate, Depositos_tiposRead
from .model_depositos_tipos import Depositos_tipos as Depositos_tiposModel
from .service_depositos_tipos import create_depositos_tipos, get_depositos_tipos, gets_depositos_tipos, delete_depositos_tipos, update_depositos_tipos
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/depositos_tipos",
    tags=["depositos_tipos"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Depositos_tiposRead, status_code=status.HTTP_201_CREATED)
async def routes_post_depositos_tipos(depositos_tipos: Depositos_tiposCreate, db: Session = Depends(get_db)):
    # Solo validamos la descripción ya que el ID es auto incremental
    if depositos_tipos.descripcion is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="La descripción es obligatoria")
    try:
        depositos_tipos_model = Depositos_tiposModel(**depositos_tipos.model_dump())
        db_depositos_tipos = create_depositos_tipos(db=db, depositos_tipos=depositos_tipos_model)
        return Depositos_tiposRead.model_validate(db_depositos_tipos)
    except Exception as e:
        logger.error(f"Error al crear Depositos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=Depositos_tiposRead)
async def routes_get_depositos_tipos_id(id: int, db: Session = Depends(get_db)):
    try:
        db_depositos_tipos = get_depositos_tipos(db, id)
        if not db_depositos_tipos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: depositos_tipos no encontrado")
        return Depositos_tiposRead.model_validate(db_depositos_tipos)
    except Exception as e:
        logger.error(f"Error al obtener Depositos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Depositos_tiposRead])
async def routes_gets_depositos_tipos_all(db: Session = Depends(get_db)):
    try:
        db_depositos_tipos = gets_depositos_tipos(db)
        # Eliminamos la validación que provoca el error 400
        # Si no hay registros, simplemente devolvemos una lista vacía
        return [Depositos_tiposRead.model_validate(depositos_tipos) for depositos_tipos in db_depositos_tipos]
    except Exception as e:
        logger.error(f"Error al obtener registros de Depositos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=Depositos_tiposRead)
async def routes_delete_depositos_tipos_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_depositos_tipos = get_depositos_tipos(db, id)
        if not resultado_depositos_tipos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: depositos_tipos no encontrado")
        db_depositos_tipos = delete_depositos_tipos(db, id)
        return Depositos_tiposRead.model_validate(db_depositos_tipos)
    except Exception as e:
        logger.error(f"Error al eliminar Depositos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=Depositos_tiposRead)
async def routes_update_depositos_tipos(id: int, depositos_tipos: Depositos_tiposUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Depositos_tipos con id = {id}")
    try:
        depositos_tipos_data = depositos_tipos.model_dump()
        db_depositos_tipos = update_depositos_tipos(db=db, id=id, depositos_tipos_data=depositos_tipos_data)
        return Depositos_tiposRead.model_validate(db_depositos_tipos)
    except Exception as e:
        logger.error(f"Error al actualizar Depositos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Corrigiendo la ruta del archivo HTML
        # La ruta correcta debe ser dentro de la carpeta depositos_tipos, no depositos
        with open(f"static/app_stock/depositos_tipos/depositos_tipos.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
