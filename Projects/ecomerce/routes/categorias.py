from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
from db.database import get_db
from security.auth_middleware import require_auth_for_template
import logging

# Imports locales del servicio
from ..schemas.categorias import CategoriasCreate, CategoriasUpdate, CategoriasRead
from ..Controllers.categorias import (
    create_categorias,
    get_categorias,
    gets_categorias,
    update_categorias,
    delete_categorias
)

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["categorias"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=CategoriasRead, status_code=status.HTTP_201_CREATED)
async def routes_post_categorias(categorias: CategoriasCreate, request: Request, user_data: dict = Depends(require_auth_for_template), db: Session = Depends(get_db)):
    try:
        # Convertir a dict y limpiar valores None/unset (especialmente PK autoincrement)
        categorias_payload = categorias.model_dump(exclude_unset=True, exclude_none=True)
        
        # Eliminar explícitamente 'id' si existe y es None (PK autoincrement)
        if 'id' in categorias_payload and categorias_payload['id'] is None:
            del categorias_payload['id']
        
        db_categorias = create_categorias(db=db, categorias=categorias_payload, user_data=user_data, request=request)
        return CategoriasRead.model_validate(db_categorias)
    except Exception as e:
        logger.error(f"Error al crear Categorias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=CategoriasRead)
async def routes_get_categorias_id(id: int, db: Session = Depends(get_db)):
    try:
        db_categorias = get_categorias(db, id)
        if not db_categorias:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: categorias no encontrado")
        return CategoriasRead.model_validate(db_categorias)
    except Exception as e:
        logger.error(f"Error al obtener Categorias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[CategoriasRead])
async def routes_gets_categorias_all(db: Session = Depends(get_db)):
    try:
        db_categorias = gets_categorias(db)
        # Una lista vacía es un resultado válido, no un error
        return [CategoriasRead.model_validate(categorias) for categorias in db_categorias]
    except Exception as e:
        logger.error(f"Error al obtener registros de Categorias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=CategoriasRead)
async def routes_delete_categorias_numero(id: int, request: Request, user_data: dict = Depends(require_auth_for_template), db: Session = Depends(get_db)):
    try:
        resultado_categorias = get_categorias(db, id)
        if not resultado_categorias:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: categorias no encontrado")
        db_categorias = delete_categorias(db, id, user_data=user_data, request=request)
        return CategoriasRead.model_validate(db_categorias)
    except Exception as e:
        logger.error(f"Error al eliminar Categorias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=CategoriasRead)
async def routes_update_categorias(id: int, categorias: CategoriasUpdate, request: Request, user_data: dict = Depends(require_auth_for_template), db: Session = Depends(get_db)):
    logger.info(f"Actualizando Categorias con id = {id}")
    try:
        categorias_data = categorias.model_dump()
        db_categorias = update_categorias(db=db, id=id, categorias_data=categorias_data, user_data=user_data, request=request)
        return CategoriasRead.model_validate(db_categorias)
    except Exception as e:
        logger.error(f"Error al actualizar Categorias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/publicas")
async def routes_gets_categorias_publicas(db: Session = Depends(get_db)):
    try:
        # Obtener todas las categorías
        db_categorias = gets_categorias(db)
        logger.info(f"Total categorías obtenidas: {len(db_categorias)}")

        # Filtrar solo categorías activas y convertir a diccionarios
        categorias_activas = []
        for c in db_categorias:
            if getattr(c, 'active', True):
                categorias_activas.append({
                    "id": c.id,
                    "nombre": c.nombre,
                    "descripcion": c.descripcion,
                    "id_padre": c.id_padre,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "active": c.active
                })

        logger.info(f"Categorías activas procesadas: {len(categorias_activas)}")
        return categorias_activas
    except Exception as e:
        logger.error(f"Error al obtener categorías públicas: {e}")
        # En lugar de lanzar error, devolver lista vacía
        return []
