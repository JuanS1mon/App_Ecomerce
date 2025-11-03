from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
from db.database import get_db
from security.auth_middleware import require_auth_for_template
import logging

# Imports locales del servicio
from ..schemas.stock import StockCreate, StockUpdate, StockRead
from ..Controllers.stock import (
    create_stock,
    get_stock,
    gets_stock,
    update_stock,
    delete_stock
)

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["stock"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=StockRead, status_code=status.HTTP_201_CREATED)
async def routes_post_stock(stock: StockCreate, request: Request, user_data: dict = Depends(require_auth_for_template), db: Session = Depends(get_db)):
    try:
        # Convertir a dict y limpiar valores None/unset (especialmente PK autoincrement)
        stock_payload = stock.model_dump(exclude_unset=True, exclude_none=True)
        
        # Eliminar explícitamente 'id' si existe y es None (PK autoincrement)
        if 'id' in stock_payload and stock_payload['id'] is None:
            del stock_payload['id']
        
        db_stock = create_stock(db=db, stock=stock_payload, user_data=user_data, request=request)
        return StockRead.model_validate(db_stock)
    except Exception as e:
        logger.error(f"Error al crear Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=StockRead)
async def routes_get_stock_id(id: int, db: Session = Depends(get_db)):
    try:
        db_stock = get_stock(db, id)
        if not db_stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: stock no encontrado")
        return StockRead.model_validate(db_stock)
    except Exception as e:
        logger.error(f"Error al obtener Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[StockRead])
async def routes_gets_stock_all(db: Session = Depends(get_db)):
    try:
        db_stock = gets_stock(db)
        # Una lista vacía es un resultado válido, no un error
        return [StockRead.model_validate(stock) for stock in db_stock]
    except Exception as e:
        logger.error(f"Error al obtener registros de Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=StockRead)
async def routes_delete_stock_numero(id: int, request: Request, user_data: dict = Depends(require_auth_for_template), db: Session = Depends(get_db)):
    try:
        resultado_stock = get_stock(db, id)
        if not resultado_stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: stock no encontrado")
        db_stock = delete_stock(db, id, user_data=user_data, request=request)
        return StockRead.model_validate(db_stock)
    except Exception as e:
        logger.error(f"Error al eliminar Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=StockRead)
async def routes_update_stock(id: int, stock: StockUpdate, request: Request, user_data: dict = Depends(require_auth_for_template), db: Session = Depends(get_db)):
    logger.info(f"Actualizando Stock con id = {id}")
    try:
        stock_data = stock.model_dump()
        db_stock = update_stock(db=db, id=id, stock_data=stock_data, user_data=user_data, request=request)
        return StockRead.model_validate(db_stock)
    except Exception as e:
        logger.error(f"Error al actualizar Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Buscar solo en la carpeta templates del proyecto
        script_dir = Path(__file__).resolve().parent
        html_path = script_dir.parent / "templates" / f"stock.html"
        if not html_path.exists():
            raise FileNotFoundError(f"No se encontró la página HTML: {html_path}")
        html_content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
