
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from .schema_depositos import DepositosCreate, DepositosUpdate, DepositosRead
from .model_depositos import Depositos as DepositosModel
from .service_depositos import create_depositos, get_depositos, gets_depositos, delete_depositos, update_depositos
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/depositos",
    tags=["depositos"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=DepositosRead, status_code=status.HTTP_201_CREATED)
async def routes_post_depositos(depositos: DepositosCreate, db: Session = Depends(get_db)):
    if depositos.id is None or depositos.descripcion is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        depositos_model = DepositosModel(**depositos.model_dump())
        db_depositos = create_depositos(db=db, depositos=depositos_model)
        return DepositosRead.model_validate(db_depositos)
    except Exception as e:
        logger.error(f"Error al crear Depositos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=DepositosRead)
async def routes_get_depositos_id(id: int, db: Session = Depends(get_db)):
    try:
        db_depositos = get_depositos(db, id)
        if not db_depositos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: depositos no encontrado")
        return DepositosRead.model_validate(db_depositos)
    except Exception as e:
        logger.error(f"Error al obtener Depositos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[DepositosRead])
async def routes_gets_depositos_all(db: Session = Depends(get_db)):
    try:
        db_depositos = gets_depositos(db)
        if not db_depositos:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: depositoss no encontrados")
        return [DepositosRead.model_validate(depositos) for depositos in db_depositos]
    except Exception as e:
        logger.error(f"Error al obtener registros de Depositos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=DepositosRead)
async def routes_delete_depositos_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_depositos = get_depositos(db, id)
        if not resultado_depositos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: depositos no encontrado")
        db_depositos = delete_depositos(db, id)
        return DepositosRead.model_validate(db_depositos)
    except Exception as e:
        logger.error(f"Error al eliminar Depositos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=DepositosRead)
async def routes_update_depositos(id: int, depositos: DepositosUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Depositos con id = {id}")
    try:
        depositos_data = depositos.model_dump()
        db_depositos = update_depositos(db=db, id=id, depositos_data=depositos_data)
        return DepositosRead.model_validate(db_depositos)
    except Exception as e:
        logger.error(f"Error al actualizar Depositos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Ruta actualizada: ahora buscamos en static/module_name/index.html
        with open(f"static/depositos/index.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
