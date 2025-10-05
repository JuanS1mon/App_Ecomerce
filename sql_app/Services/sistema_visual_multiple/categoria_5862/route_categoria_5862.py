# ============================================================================
# ROUTER: CATEGORIA_5862
# ============================================================================
"""
Router FastAPI para categoria_5862
Parte del servicio: sistema_visual_multiple
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_categoria_5862 import categoria_5862_service
from .schema_categoria_5862 import Categoria_5862, Categoria_5862Create, Categoria_5862Update

router = APIRouter(
    prefix="/categoria_5862",
    tags=["categoria_5862"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Categoria_5862, status_code=status.HTTP_201_CREATED)
def create_categoria_5862(
    obj_in: Categoria_5862Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo categoria_5862"""
    return categoria_5862_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Categoria_5862])
def read_categoria_5862_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de categoria_5862"""
    return categoria_5862_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Categoria_5862)
def read_categoria_5862(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener categoria_5862 por id"""
    db_obj = categoria_5862_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria_5862 no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Categoria_5862)
def update_categoria_5862(
    id: int,
    obj_in: Categoria_5862Update,
    db: Session = Depends(get_db)
):
    """Actualizar categoria_5862"""
    db_obj = categoria_5862_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria_5862 no encontrado"
        )
    return categoria_5862_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_categoria_5862(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar categoria_5862"""
    success = categoria_5862_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria_5862 no encontrado"
        )
