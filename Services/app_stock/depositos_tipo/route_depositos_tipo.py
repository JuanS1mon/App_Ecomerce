
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from .schema_depositos_tipo import Depositos_tipoCreate, Depositos_tipoUpdate, Depositos_tipoRead
from .model_depositos_tipo import Depositos_tipo as Depositos_tipoModel
from .service_depositos_tipo import create_depositos_tipo, get_depositos_tipo, gets_depositos_tipo, delete_depositos_tipo, update_depositos_tipo
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/depositos_tipo",
    tags=["depositos_tipo"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Depositos_tipoRead, status_code=status.HTTP_201_CREATED)
async def routes_post_depositos_tipo(depositos_tipo: Depositos_tipoCreate, db: Session = Depends(get_db)):
    if depositos_tipo.id is None or depositos_tipo.descripcion is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        depositos_tipo_model = Depositos_tipoModel(**depositos_tipo.model_dump())
        db_depositos_tipo = create_depositos_tipo(db=db, depositos_tipo=depositos_tipo_model)
        return Depositos_tipoRead.model_validate(db_depositos_tipo)
    except Exception as e:
        logger.error(f"Error al crear Depositos_tipo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=Depositos_tipoRead)
async def routes_get_depositos_tipo_id(id: int, db: Session = Depends(get_db)):
    try:
        db_depositos_tipo = get_depositos_tipo(db, id)
        if not db_depositos_tipo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: depositos_tipo no encontrado")
        return Depositos_tipoRead.model_validate(db_depositos_tipo)
    except Exception as e:
        logger.error(f"Error al obtener Depositos_tipo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Depositos_tipoRead])
async def routes_gets_depositos_tipo_all(db: Session = Depends(get_db)):
    try:
        db_depositos_tipo = gets_depositos_tipo(db)
        if not db_depositos_tipo:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: depositos_tipos no encontrados")
        return [Depositos_tipoRead.model_validate(depositos_tipo) for depositos_tipo in db_depositos_tipo]
    except Exception as e:
        logger.error(f"Error al obtener registros de Depositos_tipo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=Depositos_tipoRead)
async def routes_delete_depositos_tipo_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_depositos_tipo = get_depositos_tipo(db, id)
        if not resultado_depositos_tipo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: depositos_tipo no encontrado")
        db_depositos_tipo = delete_depositos_tipo(db, id)
        return Depositos_tipoRead.model_validate(db_depositos_tipo)
    except Exception as e:
        logger.error(f"Error al eliminar Depositos_tipo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=Depositos_tipoRead)
async def routes_update_depositos_tipo(id: int, depositos_tipo: Depositos_tipoUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Depositos_tipo con id = {id}")
    try:
        depositos_tipo_data = depositos_tipo.model_dump()
        db_depositos_tipo = update_depositos_tipo(db=db, id=id, depositos_tipo_data=depositos_tipo_data)
        return Depositos_tipoRead.model_validate(db_depositos_tipo)
    except Exception as e:
        logger.error(f"Error al actualizar Depositos_tipo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Considerar si quieres cambiar la ubicación HTML para servicios
        with open("static/html/depositos_tipo.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
