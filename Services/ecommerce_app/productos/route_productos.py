# ============================================================================
# ROUTER: PRODUCTOS
# ============================================================================
"""
Router FastAPI para productos
Parte del servicio: ecommerce_app
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_productos import productos_service
from .schema_productos import Productos, ProductosCreate, ProductosUpdate

router = APIRouter(
    prefix="/productos",
    tags=["productos"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Productos, status_code=status.HTTP_201_CREATED)
def create_productos(
    obj_in: ProductosCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo productos"""
    return productos_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Productos])
def read_productos_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de productos"""
    return productos_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Productos)
def read_productos(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener productos por id"""
    db_obj = productos_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Productos no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Productos)
def update_productos(
    id: int,
    obj_in: ProductosUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar productos"""
    db_obj = productos_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Productos no encontrado"
        )
    return productos_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_productos(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar productos"""
    success = productos_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Productos no encontrado"
        )
