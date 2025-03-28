
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_facu import FacuCreate, FacuUpdate, FacuRead
from db.models.facu import Facu as FacuModel
from db.crud.Maestro.Crud_facu import create_facu, get_facu, gets_facu, delete_facu, update_facu
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/facu",
    tags=["facu"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=FacuRead, status_code=status.HTTP_201_CREATED)
async def routes_post_facu(facu: FacuCreate, db: Session = Depends(get_db)):
    if facu.id is None or facu.asd is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        facu_model = FacuModel(**facu.model_dump())
        db_facu = create_facu(db=db, facu=facu_model)
        return FacuRead.model_validate(db_facu)
    except Exception as e:
        logger.error(f"Error al crear Facu: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=FacuRead)
async def routes_get_facu_id(id: int, db: Session = Depends(get_db)):
    try:
        db_facu = get_facu(db, id)
        if not db_facu:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: facu no encontrado")
        return FacuRead.model_validate(db_facu)
    except Exception as e:
        logger.error(f"Error al obtener Facu: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[FacuRead])
async def routes_gets_facu_all(db: Session = Depends(get_db)):
    try:
        db_facu = gets_facu(db)
        if not db_facu:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: facus no encontrados")
        return [FacuRead.model_validate(facu) for facu in db_facu]
    except Exception as e:
        logger.error(f"Error al obtener registros de Facu: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=FacuRead)
async def routes_delete_facu_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_facu = get_facu(db, id)
        if not resultado_facu:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: facu no encontrado")
        db_facu = delete_facu(db, id)
        return FacuRead.model_validate(db_facu)
    except Exception as e:
        logger.error(f"Error al eliminar Facu: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=FacuRead)
async def routes_update_facu(id: int, facu: FacuUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Facu con id = {id}")
    try:
        facu_data = facu.model_dump()
        db_facu = update_facu(db=db, id=id, facu_data=facu_data)
        return FacuRead.model_validate(db_facu)
    except Exception as e:
        logger.error(f"Error al actualizar Facu: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/facu.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
