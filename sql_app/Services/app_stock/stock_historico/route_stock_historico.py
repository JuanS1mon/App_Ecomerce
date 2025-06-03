
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from .schema_stock_historico import Stock_historicoCreate, Stock_historicoUpdate, Stock_historicoRead
from .model_stock_historico import Stock_historico as Stock_historicoModel
from .service_stock_historico import create_stock_historico, get_stock_historico, gets_stock_historico, delete_stock_historico, update_stock_historico
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/stock_historico",
    tags=["stock_historico"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=Stock_historicoRead, status_code=status.HTTP_201_CREATED)
async def routes_post_stock_historico(stock_historico: Stock_historicoCreate, db: Session = Depends(get_db)):
    if stock_historico.id is None or stock_historico.nro_movimiento is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        stock_historico_model = Stock_historicoModel(**stock_historico.model_dump())
        db_stock_historico = create_stock_historico(db=db, stock_historico=stock_historico_model)
        return Stock_historicoRead.model_validate(db_stock_historico)
    except Exception as e:
        logger.error(f"Error al crear Stock_historico: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=Stock_historicoRead)
async def routes_get_stock_historico_id(id: int, db: Session = Depends(get_db)):
    try:
        db_stock_historico = get_stock_historico(db, id)
        if not db_stock_historico:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: stock_historico no encontrado")
        return Stock_historicoRead.model_validate(db_stock_historico)
    except Exception as e:
        logger.error(f"Error al obtener Stock_historico: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[Stock_historicoRead])
async def routes_gets_stock_historico_all(db: Session = Depends(get_db)):
    try:
        db_stock_historico = gets_stock_historico(db)
        if not db_stock_historico:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: stock_historicos no encontrados")
        return [Stock_historicoRead.model_validate(stock_historico) for stock_historico in db_stock_historico]
    except Exception as e:
        logger.error(f"Error al obtener registros de Stock_historico: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=Stock_historicoRead)
async def routes_delete_stock_historico_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_stock_historico = get_stock_historico(db, id)
        if not resultado_stock_historico:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: stock_historico no encontrado")
        db_stock_historico = delete_stock_historico(db, id)
        return Stock_historicoRead.model_validate(db_stock_historico)
    except Exception as e:
        logger.error(f"Error al eliminar Stock_historico: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=Stock_historicoRead)
async def routes_update_stock_historico(id: int, stock_historico: Stock_historicoUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Stock_historico con id = {id}")
    try:
        stock_historico_data = stock_historico.model_dump()
        db_stock_historico = update_stock_historico(db=db, id=id, stock_historico_data=stock_historico_data)
        return Stock_historicoRead.model_validate(db_stock_historico)
    except Exception as e:
        logger.error(f"Error al actualizar Stock_historico: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Ruta actualizada: ahora buscamos en static/module_name/index.html
        with open(f"static/stock_historico/index.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
