
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from .schema_prueba2 import Prueba2Create, Prueba2Update, Prueba2Read
from .model_prueba2 import Prueba2 as Prueba2Model
from .service_prueba2 import create_prueba2, get_prueba2, gets_prueba2, delete_prueba2, update_prueba2
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/prueba2",
    tags=["prueba2"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Prueba2Read, status_code=status.HTTP_201_CREATED)
async def routes_post_prueba2(prueba2: Prueba2Create, db: Session = Depends(get_db)):
    if prueba2.id is None or prueba2.coa is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        prueba2_model = Prueba2Model(**prueba2.model_dump())
        db_prueba2 = create_prueba2(db=db, prueba2=prueba2_model)
        return Prueba2Read.model_validate(db_prueba2)
    except Exception as e:
        logger.error(f"Error al crear Prueba2: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=Prueba2Read)
async def routes_get_prueba2_id(id: int, db: Session = Depends(get_db)):
    try:
        db_prueba2 = get_prueba2(db, id)
        if not db_prueba2:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: prueba2 no encontrado")
        return Prueba2Read.model_validate(db_prueba2)
    except Exception as e:
        logger.error(f"Error al obtener Prueba2: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Prueba2Read])
async def routes_gets_prueba2_all(db: Session = Depends(get_db)):
    try:
        db_prueba2 = gets_prueba2(db)
        if not db_prueba2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: prueba2s no encontrados")
        return [Prueba2Read.model_validate(prueba2) for prueba2 in db_prueba2]
    except Exception as e:
        logger.error(f"Error al obtener registros de Prueba2: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=Prueba2Read)
async def routes_delete_prueba2_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_prueba2 = get_prueba2(db, id)
        if not resultado_prueba2:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: prueba2 no encontrado")
        db_prueba2 = delete_prueba2(db, id)
        return Prueba2Read.model_validate(db_prueba2)
    except Exception as e:
        logger.error(f"Error al eliminar Prueba2: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=Prueba2Read)
async def routes_update_prueba2(id: int, prueba2: Prueba2Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Prueba2 con id = {id}")
    try:
        prueba2_data = prueba2.model_dump()
        db_prueba2 = update_prueba2(db=db, id=id, prueba2_data=prueba2_data)
        return Prueba2Read.model_validate(db_prueba2)
    except Exception as e:
        logger.error(f"Error al actualizar Prueba2: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Considerar si quieres cambiar la ubicación HTML para servicios
        with open("static/html/prueba2.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
