# ============================================================================
# ROUTER: ORDEN_2650
# ============================================================================
"""
Router FastAPI para orden_2650
Parte del servicio: dm3
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_orden_2650 import orden_2650_service
from .schema_orden_2650 import Orden_2650, Orden_2650Create, Orden_2650Update

router = APIRouter(
    prefix="/orden_2650",
    tags=["orden_2650"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Orden_2650, status_code=status.HTTP_201_CREATED)
def create_orden_2650(
    obj_in: Orden_2650Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo orden_2650"""
    return orden_2650_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Orden_2650])
def read_orden_2650_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de orden_2650"""
    return orden_2650_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Orden_2650)
def read_orden_2650(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener orden_2650 por id"""
    db_obj = orden_2650_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Orden_2650 no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Orden_2650)
def update_orden_2650(
    id: int,
    obj_in: Orden_2650Update,
    db: Session = Depends(get_db)
):
    """Actualizar orden_2650"""
    db_obj = orden_2650_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Orden_2650 no encontrado"
        )
    return orden_2650_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_orden_2650(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar orden_2650"""
    success = orden_2650_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Orden_2650 no encontrado"
        )
