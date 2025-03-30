
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from .schema_stock_current import Stock_currentCreate, Stock_currentUpdate, Stock_currentRead
from .model_stock_current import Stock_current as Stock_currentModel
from .service_stock_current import create_stock_current, get_stock_current, gets_stock_current, delete_stock_current, update_stock_current
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/stock_current",
    tags=["stock_current"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Stock_currentRead, status_code=status.HTTP_201_CREATED)
async def routes_post_stock_current(stock_current: Stock_currentCreate, db: Session = Depends(get_db)):
    if stock_current.id is None or stock_current.nro_movimiento is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        stock_current_model = Stock_currentModel(**stock_current.model_dump())
        db_stock_current = create_stock_current(db=db, stock_current=stock_current_model)
        return Stock_currentRead.model_validate(db_stock_current)
    except Exception as e:
        logger.error(f"Error al crear Stock_current: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=Stock_currentRead)
async def routes_get_stock_current_id(id: int, db: Session = Depends(get_db)):
    try:
        db_stock_current = get_stock_current(db, id)
        if not db_stock_current:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: stock_current no encontrado")
        return Stock_currentRead.model_validate(db_stock_current)
    except Exception as e:
        logger.error(f"Error al obtener Stock_current: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Stock_currentRead])
async def routes_gets_stock_current_all(db: Session = Depends(get_db)):
    try:
        db_stock_current = gets_stock_current(db)
        if not db_stock_current:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: stock_currents no encontrados")
        return [Stock_currentRead.model_validate(stock_current) for stock_current in db_stock_current]
    except Exception as e:
        logger.error(f"Error al obtener registros de Stock_current: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=Stock_currentRead)
async def routes_delete_stock_current_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_stock_current = get_stock_current(db, id)
        if not resultado_stock_current:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: stock_current no encontrado")
        db_stock_current = delete_stock_current(db, id)
        return Stock_currentRead.model_validate(db_stock_current)
    except Exception as e:
        logger.error(f"Error al eliminar Stock_current: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=Stock_currentRead)
async def routes_update_stock_current(id: int, stock_current: Stock_currentUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Stock_current con id = {id}")
    try:
        stock_current_data = stock_current.model_dump()
        db_stock_current = update_stock_current(db=db, id=id, stock_current_data=stock_current_data)
        return Stock_currentRead.model_validate(db_stock_current)
    except Exception as e:
        logger.error(f"Error al actualizar Stock_current: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Considerar si quieres cambiar la ubicación HTML para servicios
        with open("static/html/stock_current.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
