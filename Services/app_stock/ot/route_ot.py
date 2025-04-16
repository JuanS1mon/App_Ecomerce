
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from .schema_ot import OtCreate, OtUpdate, OtRead
from .model_ot import Ot as OtModel
from .service_ot import create_ot, get_ot, gets_ot, delete_ot, update_ot
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ot",
    tags=["ot"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=OtRead, status_code=status.HTTP_201_CREATED)
async def routes_post_ot(ot: OtCreate, db: Session = Depends(get_db)):
    if ot.id is None or ot.id_trabajo is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        ot_model = OtModel(**ot.model_dump())
        db_ot = create_ot(db=db, ot=ot_model)
        return OtRead.model_validate(db_ot)
    except Exception as e:
        logger.error(f"Error al crear Ot: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=OtRead)
async def routes_get_ot_id(id: int, db: Session = Depends(get_db)):
    try:
        db_ot = get_ot(db, id)
        if not db_ot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: ot no encontrado")
        return OtRead.model_validate(db_ot)
    except Exception as e:
        logger.error(f"Error al obtener Ot: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[OtRead])
async def routes_gets_ot_all(db: Session = Depends(get_db)):
    try:
        db_ot = gets_ot(db)
        if not db_ot:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: ots no encontrados")
        return [OtRead.model_validate(ot) for ot in db_ot]
    except Exception as e:
        logger.error(f"Error al obtener registros de Ot: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=OtRead)
async def routes_delete_ot_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_ot = get_ot(db, id)
        if not resultado_ot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: ot no encontrado")
        db_ot = delete_ot(db, id)
        return OtRead.model_validate(db_ot)
    except Exception as e:
        logger.error(f"Error al eliminar Ot: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=OtRead)
async def routes_update_ot(id: int, ot: OtUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Ot con id = {id}")
    try:
        ot_data = ot.model_dump()
        db_ot = update_ot(db=db, id=id, ot_data=ot_data)
        return OtRead.model_validate(db_ot)
    except Exception as e:
        logger.error(f"Error al actualizar Ot: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Ruta actualizada: ahora buscamos en static/module_name/index.html
        with open(f"static/ot/index.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
