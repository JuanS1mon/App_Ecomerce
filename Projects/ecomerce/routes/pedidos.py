from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
from db.database import get_db
from security.auth_middleware import require_auth_for_template
import logging

# Imports locales del servicio
from ..schemas.pedidos import PedidosCreate, PedidosUpdate, PedidosRead
from ..Controllers.pedidos import (
    create_pedidos,
    get_pedidos,
    gets_pedidos,
    update_pedidos,
    delete_pedidos
)

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["pedidos"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=PedidosRead, status_code=status.HTTP_201_CREATED)
async def routes_post_pedidos(pedidos: PedidosCreate, request: Request, user_data: dict = Depends(require_auth_for_template), db: Session = Depends(get_db)):
    try:
        # Convertir a dict y limpiar valores None/unset (especialmente PK autoincrement)
        pedidos_payload = pedidos.model_dump(exclude_unset=True, exclude_none=True)
        
        # Eliminar explícitamente 'id' si existe y es None (PK autoincrement)
        if 'id' in pedidos_payload and pedidos_payload['id'] is None:
            del pedidos_payload['id']
        
        db_pedidos = create_pedidos(db=db, pedidos=pedidos_payload, user_data=user_data, request=request)
        return PedidosRead.model_validate(db_pedidos)
    except Exception as e:
        logger.error(f"Error al crear Pedidos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=PedidosRead)
async def routes_get_pedidos_id(id: int, db: Session = Depends(get_db)):
    try:
        db_pedidos = get_pedidos(db, id)
        if not db_pedidos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: pedidos no encontrado")
        return PedidosRead.model_validate(db_pedidos)
    except Exception as e:
        logger.error(f"Error al obtener Pedidos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[PedidosRead])
async def routes_gets_pedidos_all(db: Session = Depends(get_db)):
    try:
        db_pedidos = gets_pedidos(db)
        # Una lista vacía es un resultado válido, no un error
        return [PedidosRead.model_validate(pedidos) for pedidos in db_pedidos]
    except Exception as e:
        logger.error(f"Error al obtener registros de Pedidos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=PedidosRead)
async def routes_delete_pedidos_numero(id: int, request: Request, user_data: dict = Depends(require_auth_for_template), db: Session = Depends(get_db)):
    try:
        resultado_pedidos = get_pedidos(db, id)
        if not resultado_pedidos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: pedidos no encontrado")
        db_pedidos = delete_pedidos(db, id, user_data=user_data, request=request)
        return PedidosRead.model_validate(db_pedidos)
    except Exception as e:
        logger.error(f"Error al eliminar Pedidos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=PedidosRead)
async def routes_update_pedidos(id: int, pedidos: PedidosUpdate, request: Request, user_data: dict = Depends(require_auth_for_template), db: Session = Depends(get_db)):
    logger.info(f"Actualizando Pedidos con id = {id}")
    try:
        pedidos_data = pedidos.model_dump()
        db_pedidos = update_pedidos(db=db, id=id, pedidos_data=pedidos_data, user_data=user_data, request=request)
        return PedidosRead.model_validate(db_pedidos)
    except Exception as e:
        logger.error(f"Error al actualizar Pedidos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Buscar solo en la carpeta templates del proyecto
        script_dir = Path(__file__).resolve().parent
        html_path = script_dir.parent / "templates" / f"pedidos.html"
        if not html_path.exists():
            raise FileNotFoundError(f"No se encontró la página HTML: {html_path}")
        html_content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")
