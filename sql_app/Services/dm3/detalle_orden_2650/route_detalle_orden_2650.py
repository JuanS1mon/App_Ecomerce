# ============================================================================
# ROUTER: DETALLE_ORDEN_2650
# ============================================================================
"""
Router FastAPI para detalle_orden_2650
Parte del servicio: dm3
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_detalle_orden_2650 import detalle_orden_2650_service
from .schema_detalle_orden_2650 import Detalle_Orden_2650, Detalle_Orden_2650Create, Detalle_Orden_2650Update

router = APIRouter(
    prefix="/detalle_orden_2650",
    tags=["detalle_orden_2650"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Detalle_Orden_2650, status_code=status.HTTP_201_CREATED)
def create_detalle_orden_2650(
    obj_in: Detalle_Orden_2650Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo detalle_orden_2650"""
    return detalle_orden_2650_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Detalle_Orden_2650])
def read_detalle_orden_2650_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de detalle_orden_2650"""
    return detalle_orden_2650_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Detalle_Orden_2650)
def read_detalle_orden_2650(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener detalle_orden_2650 por id"""
    db_obj = detalle_orden_2650_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detalle_Orden_2650 no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Detalle_Orden_2650)
def update_detalle_orden_2650(
    id: int,
    obj_in: Detalle_Orden_2650Update,
    db: Session = Depends(get_db)
):
    """Actualizar detalle_orden_2650"""
    db_obj = detalle_orden_2650_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detalle_Orden_2650 no encontrado"
        )
    return detalle_orden_2650_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_detalle_orden_2650(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar detalle_orden_2650"""
    success = detalle_orden_2650_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detalle_Orden_2650 no encontrado"
        )
