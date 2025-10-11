# ============================================================================
# ROUTER: ORDEN_5372
# ============================================================================
"""
Router FastAPI para orden_5372
Parte del servicio: sistema_visual_multiple
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from .service_orden_5372 import orden_5372_service
from .schema_orden_5372 import Orden_5372, Orden_5372Create, Orden_5372Update

router = APIRouter(
    prefix="/orden_5372",
    tags=["orden_5372"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Orden_5372, status_code=status.HTTP_201_CREATED)
def create_orden_5372(
    obj_in: Orden_5372Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo orden_5372"""
    return orden_5372_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Orden_5372])
def read_orden_5372_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de orden_5372"""
    return orden_5372_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Orden_5372)
def read_orden_5372(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener orden_5372 por id"""
    db_obj = orden_5372_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Orden_5372 no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Orden_5372)
def update_orden_5372(
    id: int,
    obj_in: Orden_5372Update,
    db: Session = Depends(get_db)
):
    """Actualizar orden_5372"""
    db_obj = orden_5372_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Orden_5372 no encontrado"
        )
    return orden_5372_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_orden_5372(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar orden_5372"""
    success = orden_5372_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Orden_5372 no encontrado"
        )
