
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from .schema_empleados import EmpleadosCreate, EmpleadosUpdate, EmpleadosRead
from .model_empleados import Empleados as EmpleadosModel
from .service_empleados import create_empleados, get_empleados, gets_empleados, delete_empleados, update_empleados
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/empleados",
    tags=["empleados"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=EmpleadosRead, status_code=status.HTTP_201_CREATED)
async def routes_post_empleados(empleados: EmpleadosCreate, db: Session = Depends(get_db)):
    if empleados.id is None or empleados.legajo is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        empleados_model = EmpleadosModel(**empleados.model_dump())
        db_empleados = create_empleados(db=db, empleados=empleados_model)
        return EmpleadosRead.model_validate(db_empleados)
    except Exception as e:
        logger.error(f"Error al crear Empleados: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=EmpleadosRead)
async def routes_get_empleados_id(id: int, db: Session = Depends(get_db)):
    try:
        db_empleados = get_empleados(db, id)
        if not db_empleados:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: empleados no encontrado")
        return EmpleadosRead.model_validate(db_empleados)
    except Exception as e:
        logger.error(f"Error al obtener Empleados: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[EmpleadosRead])
async def routes_gets_empleados_all(db: Session = Depends(get_db)):
    try:
        db_empleados = gets_empleados(db)
        if not db_empleados:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: empleadoss no encontrados")
        return [EmpleadosRead.model_validate(empleados) for empleados in db_empleados]
    except Exception as e:
        logger.error(f"Error al obtener registros de Empleados: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=EmpleadosRead)
async def routes_delete_empleados_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_empleados = get_empleados(db, id)
        if not resultado_empleados:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: empleados no encontrado")
        db_empleados = delete_empleados(db, id)
        return EmpleadosRead.model_validate(db_empleados)
    except Exception as e:
        logger.error(f"Error al eliminar Empleados: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=EmpleadosRead)
async def routes_update_empleados(id: int, empleados: EmpleadosUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Empleados con id = {id}")
    try:
        empleados_data = empleados.model_dump()
        db_empleados = update_empleados(db=db, id=id, empleados_data=empleados_data)
        return EmpleadosRead.model_validate(db_empleados)
    except Exception as e:
        logger.error(f"Error al actualizar Empleados: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Considerar si quieres cambiar la ubicación HTML para servicios
        with open("static/html/empleados.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
