# ============================================================================
# ROUTER: PRODUCTO_2650
# ============================================================================
"""
Router FastAPI para producto_2650
Parte del servicio: dm3
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_producto_2650 import producto_2650_service
from .schema_producto_2650 import Producto_2650, Producto_2650Create, Producto_2650Update

router = APIRouter(
    prefix="/producto_2650",
    tags=["producto_2650"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Producto_2650, status_code=status.HTTP_201_CREATED)
def create_producto_2650(
    obj_in: Producto_2650Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo producto_2650"""
    return producto_2650_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Producto_2650])
def read_producto_2650_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de producto_2650"""
    return producto_2650_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Producto_2650)
def read_producto_2650(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener producto_2650 por id"""
    db_obj = producto_2650_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto_2650 no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Producto_2650)
def update_producto_2650(
    id: int,
    obj_in: Producto_2650Update,
    db: Session = Depends(get_db)
):
    """Actualizar producto_2650"""
    db_obj = producto_2650_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto_2650 no encontrado"
        )
    return producto_2650_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto_2650(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar producto_2650"""
    success = producto_2650_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto_2650 no encontrado"
        )
