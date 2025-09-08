# ============================================================================
# ROUTER: CATEGORIA_2650
# ============================================================================
"""
Router FastAPI para categoria_2650
Parte del servicio: dm3
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_categoria_2650 import categoria_2650_service
from .schema_categoria_2650 import Categoria_2650, Categoria_2650Create, Categoria_2650Update

router = APIRouter(
    prefix="/categoria_2650",
    tags=["categoria_2650"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Categoria_2650, status_code=status.HTTP_201_CREATED)
def create_categoria_2650(
    obj_in: Categoria_2650Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo categoria_2650"""
    return categoria_2650_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Categoria_2650])
def read_categoria_2650_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de categoria_2650"""
    return categoria_2650_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Categoria_2650)
def read_categoria_2650(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener categoria_2650 por id"""
    db_obj = categoria_2650_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria_2650 no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Categoria_2650)
def update_categoria_2650(
    id: int,
    obj_in: Categoria_2650Update,
    db: Session = Depends(get_db)
):
    """Actualizar categoria_2650"""
    db_obj = categoria_2650_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria_2650 no encontrado"
        )
    return categoria_2650_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_categoria_2650(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar categoria_2650"""
    success = categoria_2650_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria_2650 no encontrado"
        )
