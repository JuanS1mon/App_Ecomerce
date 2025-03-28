
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from .schema_prueba3 import Prueba3Create, Prueba3Update, Prueba3Read
from .model_prueba3 import Prueba3 as Prueba3Model
from .service_prueba3 import create_prueba3, get_prueba3, gets_prueba3, delete_prueba3, update_prueba3
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/prueba3",
    tags=["prueba3"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Prueba3Read, status_code=status.HTTP_201_CREATED)
async def routes_post_prueba3(prueba3: Prueba3Create, db: Session = Depends(get_db)):
    if prueba3.id is None or prueba3.test1 is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        prueba3_model = Prueba3Model(**prueba3.model_dump())
        db_prueba3 = create_prueba3(db=db, prueba3=prueba3_model)
        return Prueba3Read.model_validate(db_prueba3)
    except Exception as e:
        logger.error(f"Error al crear Prueba3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=Prueba3Read)
async def routes_get_prueba3_id(id: int, db: Session = Depends(get_db)):
    try:
        db_prueba3 = get_prueba3(db, id)
        if not db_prueba3:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: prueba3 no encontrado")
        return Prueba3Read.model_validate(db_prueba3)
    except Exception as e:
        logger.error(f"Error al obtener Prueba3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Prueba3Read])
async def routes_gets_prueba3_all(db: Session = Depends(get_db)):
    try:
        db_prueba3 = gets_prueba3(db)
        if not db_prueba3:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: prueba3s no encontrados")
        return [Prueba3Read.model_validate(prueba3) for prueba3 in db_prueba3]
    except Exception as e:
        logger.error(f"Error al obtener registros de Prueba3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=Prueba3Read)
async def routes_delete_prueba3_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_prueba3 = get_prueba3(db, id)
        if not resultado_prueba3:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: prueba3 no encontrado")
        db_prueba3 = delete_prueba3(db, id)
        return Prueba3Read.model_validate(db_prueba3)
    except Exception as e:
        logger.error(f"Error al eliminar Prueba3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=Prueba3Read)
async def routes_update_prueba3(id: int, prueba3: Prueba3Update, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Prueba3 con id = {id}")
    try:
        prueba3_data = prueba3.model_dump()
        db_prueba3 = update_prueba3(db=db, id=id, prueba3_data=prueba3_data)
        return Prueba3Read.model_validate(db_prueba3)
    except Exception as e:
        logger.error(f"Error al actualizar Prueba3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Considerar si quieres cambiar la ubicación HTML para servicios
        with open("static/html/prueba3.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
