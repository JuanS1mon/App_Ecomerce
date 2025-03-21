
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas.Maestro.Schema_a import ACreate, AUpdate, ARead
from db.models.a import A as AModel
from db.crud.Maestro.Crud_a import create_a, get_a, gets_a, delete_a, update_a
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/a",
    tags=["a"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=ARead, status_code=status.HTTP_201_CREATED)
async def routes_post_a(a: ACreate, db: Session = Depends(get_db)):
    if a.id is None or a.codigo is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        a_model = AModel(**a.model_dump())
        db_a = create_a(db=db, a=a_model)
        return ARead.model_validate(db_a)
    except Exception as e:
        logger.error(f"Error al crear A: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=ARead)
async def routes_get_a_id(id: int, db: Session = Depends(get_db)):
    try:
        db_a = get_a(db, id)
        if not db_a:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: a no encontrado")
        return ARead.model_validate(db_a)
    except Exception as e:
        logger.error(f"Error al obtener A: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[ARead])
async def routes_gets_a_all(db: Session = Depends(get_db)):
    try:
        db_a = gets_a(db)
        if not db_a:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: as no encontrados")
        return [ARead.model_validate(a) for a in db_a]
    except Exception as e:
        logger.error(f"Error al obtener registros de A: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=ARead)
async def routes_delete_a_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_a = get_a(db, id)
        if not resultado_a:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: a no encontrado")
        db_a = delete_a(db, id)
        return ARead.model_validate(db_a)
    except Exception as e:
        logger.error(f"Error al eliminar A: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=ARead)
async def routes_update_a(id: int, a: AUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando A con id = {id}")
    try:
        a_data = a.model_dump()
        db_a = update_a(db=db, id=id, a_data=a_data)
        return ARead.model_validate(db_a)
    except Exception as e:
        logger.error(f"Error al actualizar A: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        with open("static/html/a.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
