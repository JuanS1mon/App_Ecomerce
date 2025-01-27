
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_carga import CargaCreate, CargaUpdate, CargaRead
from db.models.carga import Carga as CargaModel
from db.crud.Maestro.Crud_carga import create_carga, get_carga, gets_carga, delete_carga, update_carga
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/carga",
    tags=["carga"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=CargaRead, status_code=status.HTTP_201_CREATED)
async def routes_post_carga(carga: CargaCreate, db: Session = Depends(get_db)):
    if carga.nrosuceso is None or carga.fecha is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        carga_model = CargaModel(**carga.model_dump())
        db_carga = create_carga(db=db, carga=carga_model)
        return CargaRead.model_validate(db_carga)
    except Exception as e:
        logger.error(f"Error al crear Carga: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{nrosuceso}", response_model=CargaRead)
async def routes_get_carga_nrosuceso(nrosuceso: int, db: Session = Depends(get_db)):
    try:
        db_carga = get_carga(db, nrosuceso)
        if not db_carga:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: carga no encontrado")
        return CargaRead.model_validate(db_carga)
    except Exception as e:
        logger.error(f"Error al obtener Carga: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[CargaRead])
async def routes_gets_carga_all(db: Session = Depends(get_db)):
    try:
        db_carga = gets_carga(db)
        if not db_carga:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: cargas no encontrados")
        return [CargaRead.model_validate(carga) for carga in db_carga]
    except Exception as e:
        logger.error(f"Error al obtener registros de Carga: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{nrosuceso}", response_model=CargaRead)
async def routes_delete_carga_numero(nrosuceso: int, db: Session = Depends(get_db)):
    try:
        resultado_carga = get_carga(db, nrosuceso)
        if not resultado_carga:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: carga no encontrado")
        db_carga = delete_carga(db, nrosuceso)
        return CargaRead.model_validate(db_carga)
    except Exception as e:
        logger.error(f"Error al eliminar Carga: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{nrosuceso}", response_model=CargaRead)
async def routes_update_carga(nrosuceso: int, carga: CargaUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Carga con nrosuceso = {nrosuceso}")
    try:
        carga_data = carga.model_dump()
        db_carga = update_carga(db=db, nrosuceso=nrosuceso, carga_data=carga_data)
        return CargaRead.model_validate(db_carga)
    except Exception as e:
        logger.error(f"Error al actualizar Carga: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/carga.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
