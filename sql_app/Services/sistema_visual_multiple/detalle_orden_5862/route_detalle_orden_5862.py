# ============================================================================
# ROUTER: DETALLE_ORDEN_5862
# ============================================================================
"""
Router FastAPI para detalle_orden_5862
Parte del servicio: sistema_visual_multiple
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_detalle_orden_5862 import detalle_orden_5862_service
from .schema_detalle_orden_5862 import Detalle_Orden_5862, Detalle_Orden_5862Create, Detalle_Orden_5862Update

router = APIRouter(
    prefix="/detalle_orden_5862",
    tags=["detalle_orden_5862"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Detalle_Orden_5862, status_code=status.HTTP_201_CREATED)
def create_detalle_orden_5862(
    obj_in: Detalle_Orden_5862Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo detalle_orden_5862"""
    return detalle_orden_5862_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Detalle_Orden_5862])
def read_detalle_orden_5862_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de detalle_orden_5862"""
    return detalle_orden_5862_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Detalle_Orden_5862)
def read_detalle_orden_5862(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener detalle_orden_5862 por id"""
    db_obj = detalle_orden_5862_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detalle_Orden_5862 no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Detalle_Orden_5862)
def update_detalle_orden_5862(
    id: int,
    obj_in: Detalle_Orden_5862Update,
    db: Session = Depends(get_db)
):
    """Actualizar detalle_orden_5862"""
    db_obj = detalle_orden_5862_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detalle_Orden_5862 no encontrado"
        )
    return detalle_orden_5862_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_detalle_orden_5862(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar detalle_orden_5862"""
    success = detalle_orden_5862_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detalle_Orden_5862 no encontrado"
        )
