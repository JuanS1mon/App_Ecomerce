# ============================================================================
# ROUTER: PRODUCTO_4096
# ============================================================================
"""
Router FastAPI para producto_4096
Parte del servicio: sist1
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from .service_producto_4096 import producto_4096_service
from .schema_producto_4096 import Producto_4096, Producto_4096Create, Producto_4096Update

router = APIRouter(
    prefix="/producto_4096",
    tags=["producto_4096"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Producto_4096, status_code=status.HTTP_201_CREATED)
def create_producto_4096(
    obj_in: Producto_4096Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo producto_4096"""
    return producto_4096_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Producto_4096])
def read_producto_4096_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de producto_4096"""
    return producto_4096_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Producto_4096)
def read_producto_4096(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener producto_4096 por id"""
    db_obj = producto_4096_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto_4096 no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Producto_4096)
def update_producto_4096(
    id: int,
    obj_in: Producto_4096Update,
    db: Session = Depends(get_db)
):
    """Actualizar producto_4096"""
    db_obj = producto_4096_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto_4096 no encontrado"
        )
    return producto_4096_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto_4096(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar producto_4096"""
    success = producto_4096_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto_4096 no encontrado"
        )
