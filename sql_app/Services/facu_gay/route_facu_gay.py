
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from .schema_facu_gay import Facu_gayCreate, Facu_gayUpdate, Facu_gayRead
from .model_facu_gay import Facu_gay as Facu_gayModel
from .service_facu_gay import create_facu_gay, get_facu_gay, gets_facu_gay, delete_facu_gay, update_facu_gay
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/facu_gay",
    tags=["facu_gay"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Facu_gayRead, status_code=status.HTTP_201_CREATED)
async def routes_post_facu_gay(facu_gay: Facu_gayCreate, db: Session = Depends(get_db)):
    if facu_gay.id is None or facu_gay.codigo is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        facu_gay_model = Facu_gayModel(**facu_gay.model_dump())
        db_facu_gay = create_facu_gay(db=db, facu_gay=facu_gay_model)
        return Facu_gayRead.model_validate(db_facu_gay)
    except Exception as e:
        logger.error(f"Error al crear Facu_gay: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=Facu_gayRead)
async def routes_get_facu_gay_id(id: int, db: Session = Depends(get_db)):
    try:
        db_facu_gay = get_facu_gay(db, id)
        if not db_facu_gay:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: facu_gay no encontrado")
        return Facu_gayRead.model_validate(db_facu_gay)
    except Exception as e:
        logger.error(f"Error al obtener Facu_gay: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Facu_gayRead])
async def routes_gets_facu_gay_all(db: Session = Depends(get_db)):
    try:
        db_facu_gay = gets_facu_gay(db)
        if not db_facu_gay:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: facu_gays no encontrados")
        return [Facu_gayRead.model_validate(facu_gay) for facu_gay in db_facu_gay]
    except Exception as e:
        logger.error(f"Error al obtener registros de Facu_gay: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=Facu_gayRead)
async def routes_delete_facu_gay_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_facu_gay = get_facu_gay(db, id)
        if not resultado_facu_gay:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: facu_gay no encontrado")
        db_facu_gay = delete_facu_gay(db, id)
        return Facu_gayRead.model_validate(db_facu_gay)
    except Exception as e:
        logger.error(f"Error al eliminar Facu_gay: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=Facu_gayRead)
async def routes_update_facu_gay(id: int, facu_gay: Facu_gayUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Facu_gay con id = {id}")
    try:
        facu_gay_data = facu_gay.model_dump()
        db_facu_gay = update_facu_gay(db=db, id=id, facu_gay_data=facu_gay_data)
        return Facu_gayRead.model_validate(db_facu_gay)
    except Exception as e:
        logger.error(f"Error al actualizar Facu_gay: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Considerar si quieres cambiar la ubicación HTML para servicios
        with open("static/html/facu_gay.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
