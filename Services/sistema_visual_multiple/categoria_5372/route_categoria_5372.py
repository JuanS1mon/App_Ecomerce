# ============================================================================
# ROUTER: CATEGORIA_5372
# ============================================================================
"""
Router FastAPI para categoria_5372
Parte del servicio: sistema_visual_multiple
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_categoria_5372 import categoria_5372_service
from .schema_categoria_5372 import Categoria_5372, Categoria_5372Create, Categoria_5372Update

router = APIRouter(
    prefix="/categoria_5372",
    tags=["categoria_5372"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Categoria_5372, status_code=status.HTTP_201_CREATED)
def create_categoria_5372(
    obj_in: Categoria_5372Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo categoria_5372"""
    return categoria_5372_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Categoria_5372])
def read_categoria_5372_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de categoria_5372"""
    return categoria_5372_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Categoria_5372)
def read_categoria_5372(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener categoria_5372 por id"""
    db_obj = categoria_5372_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria_5372 no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Categoria_5372)
def update_categoria_5372(
    id: int,
    obj_in: Categoria_5372Update,
    db: Session = Depends(get_db)
):
    """Actualizar categoria_5372"""
    db_obj = categoria_5372_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria_5372 no encontrado"
        )
    return categoria_5372_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_categoria_5372(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar categoria_5372"""
    success = categoria_5372_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria_5372 no encontrado"
        )
