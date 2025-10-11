# ============================================================================
# ROUTER: ORDEN_4096
# ============================================================================
"""
Router FastAPI para orden_4096
Parte del servicio: sist1
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from .service_orden_4096 import orden_4096_service
from .schema_orden_4096 import Orden_4096, Orden_4096Create, Orden_4096Update

router = APIRouter(
    prefix="/orden_4096",
    tags=["orden_4096"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Orden_4096, status_code=status.HTTP_201_CREATED)
def create_orden_4096(
    obj_in: Orden_4096Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo orden_4096"""
    return orden_4096_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Orden_4096])
def read_orden_4096_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de orden_4096"""
    return orden_4096_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Orden_4096)
def read_orden_4096(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener orden_4096 por id"""
    db_obj = orden_4096_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Orden_4096 no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Orden_4096)
def update_orden_4096(
    id: int,
    obj_in: Orden_4096Update,
    db: Session = Depends(get_db)
):
    """Actualizar orden_4096"""
    db_obj = orden_4096_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Orden_4096 no encontrado"
        )
    return orden_4096_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_orden_4096(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar orden_4096"""
    success = orden_4096_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Orden_4096 no encontrado"
        )
