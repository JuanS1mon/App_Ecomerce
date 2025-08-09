# ============================================================================
# ROUTER: DETALLE_ORDEN
# ============================================================================
"""
Router FastAPI para detalle_orden
Parte del servicio: ecommerce_app
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_detalle_orden import detalle_orden_service
from .schema_detalle_orden import Detalle_Orden, Detalle_OrdenCreate, Detalle_OrdenUpdate

router = APIRouter(
    prefix="/detalle_orden",
    tags=["detalle_orden"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Detalle_Orden, status_code=status.HTTP_201_CREATED)
def create_detalle_orden(
    obj_in: Detalle_OrdenCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo detalle_orden"""
    return detalle_orden_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Detalle_Orden])
def read_detalle_orden_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de detalle_orden"""
    return detalle_orden_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Detalle_Orden)
def read_detalle_orden(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener detalle_orden por id"""
    db_obj = detalle_orden_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detalle_Orden no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Detalle_Orden)
def update_detalle_orden(
    id: int,
    obj_in: Detalle_OrdenUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar detalle_orden"""
    db_obj = detalle_orden_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detalle_Orden no encontrado"
        )
    return detalle_orden_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_detalle_orden(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar detalle_orden"""
    success = detalle_orden_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detalle_Orden no encontrado"
        )
