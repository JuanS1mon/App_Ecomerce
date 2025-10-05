# ============================================================================
# ROUTER: PRODUCTO_5862
# ============================================================================
"""
Router FastAPI para producto_5862
Parte del servicio: sistema_visual_multiple
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_producto_5862 import producto_5862_service
from .schema_producto_5862 import Producto_5862, Producto_5862Create, Producto_5862Update

router = APIRouter(
    prefix="/producto_5862",
    tags=["producto_5862"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Producto_5862, status_code=status.HTTP_201_CREATED)
def create_producto_5862(
    obj_in: Producto_5862Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo producto_5862"""
    return producto_5862_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Producto_5862])
def read_producto_5862_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de producto_5862"""
    return producto_5862_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Producto_5862)
def read_producto_5862(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener producto_5862 por id"""
    db_obj = producto_5862_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto_5862 no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Producto_5862)
def update_producto_5862(
    id: int,
    obj_in: Producto_5862Update,
    db: Session = Depends(get_db)
):
    """Actualizar producto_5862"""
    db_obj = producto_5862_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto_5862 no encontrado"
        )
    return producto_5862_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto_5862(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar producto_5862"""
    success = producto_5862_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto_5862 no encontrado"
        )
