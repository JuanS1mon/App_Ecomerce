from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from pathlib import Path
from db.database import get_db
from security.auth_middleware import require_auth_for_template
import logging

# Imports locales del servicio
from ..schemas.carritos import CarritosCreate, CarritosUpdate, CarritosRead
from ..models.carritos import EcomerceCarritos
from ..Controllers.carritos import (
    create_carritos,
    get_carritos,
    gets_carritos,
    update_carritos,
    delete_carritos
)

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["carritos"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=CarritosRead, status_code=status.HTTP_201_CREATED)
async def routes_post_carritos(carritos: CarritosCreate, request: Request, user_data: dict = Depends(require_auth_for_template), db: Session = Depends(get_db)):
    try:
        # Convertir a dict y limpiar valores None/unset (especialmente PK autoincrement)
        carritos_payload = carritos.model_dump(exclude_unset=True, exclude_none=True)
        
        # Eliminar explícitamente 'id' si existe y es None (PK autoincrement)
        if 'id' in carritos_payload and carritos_payload['id'] is None:
            del carritos_payload['id']
        
        db_carritos = create_carritos(db=db, carritos=carritos_payload, user_data=user_data, request=request)
        return CarritosRead.model_validate(db_carritos)
    except Exception as e:
        logger.error(f"Error al crear Carritos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=CarritosRead)
async def routes_get_carritos_id(id: int, db: Session = Depends(get_db)):
    try:
        db_carritos = get_carritos(db, id)
        if not db_carritos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: carritos no encontrado")
        return CarritosRead.model_validate(db_carritos)
    except Exception as e:
        logger.error(f"Error al obtener Carritos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[CarritosRead])
async def routes_gets_carritos_all(db: Session = Depends(get_db)):
    try:
        db_carritos = gets_carritos(db)
        # Una lista vacía es un resultado válido, no un error
        return [CarritosRead.model_validate(carritos) for carritos in db_carritos]
    except Exception as e:
        logger.error(f"Error al obtener registros de Carritos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=CarritosRead)
async def routes_delete_carritos_numero(id: int, request: Request, user_data: dict = Depends(require_auth_for_template), db: Session = Depends(get_db)):
    try:
        resultado_carritos = get_carritos(db, id)
        if not resultado_carritos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: carritos no encontrado")
        db_carritos = delete_carritos(db, id, user_data=user_data, request=request)
        return CarritosRead.model_validate(db_carritos)
    except Exception as e:
        logger.error(f"Error al eliminar Carritos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=CarritosRead)
async def routes_update_carritos(id: int, carritos: CarritosUpdate, request: Request, user_data: dict = Depends(require_auth_for_template), db: Session = Depends(get_db)):
    logger.info(f"Actualizando Carritos con id = {id}")
    try:
        carritos_data = carritos.model_dump()
        db_carritos = update_carritos(db=db, id=id, carritos_data=carritos_data, user_data=user_data, request=request)
        return CarritosRead.model_validate(db_carritos)
    except Exception as e:
        logger.error(f"Error al actualizar Carritos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Buscar solo en la carpeta templates del proyecto
        script_dir = Path(__file__).resolve().parent
        html_path = script_dir.parent / "templates" / f"carritos.html"
        if not html_path.exists():
            raise FileNotFoundError(f"No se encontró la página HTML: {html_path}")
        html_content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")

@router.get("/activo/{user_id}", response_model=CarritosRead)
async def routes_get_carrito_activo(user_id: int, db: Session = Depends(get_db)):
    try:
        # Obtener el carrito activo del usuario
        result = db.execute(
            text("SELECT TOP 1 id, id_usuario, estado, created_at FROM ecomerce_carritos WHERE id_usuario = :user_id AND estado = 'activo' ORDER BY created_at DESC"),
            {"user_id": user_id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró carrito activo para el usuario")
        
        # Crear el objeto directamente con los valores
        carritos = EcomerceCarritos()
        carritos.id = result[0]
        carritos.id_usuario = result[1]
        carritos.estado = result[2]
        carritos.created_at = result[3]
        
        return CarritosRead.model_validate(carritos)
    except Exception as e:
        logger.error(f"Error al obtener carrito activo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el carrito activo.")
