# ============================================================================
# ROUTER: ORDEN_7306
# ============================================================================
"""
Router FastAPI para orden_7306
Parte del servicio: sistema_visual_multiple
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_orden_7306 import orden_7306_service
from .schema_orden_7306 import Orden_7306, Orden_7306Create, Orden_7306Update

router = APIRouter(
    prefix="/orden_7306",
    tags=["orden_7306"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Orden_7306, status_code=status.HTTP_201_CREATED)
def create_orden_7306(
    obj_in: Orden_7306Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo orden_7306"""
    return orden_7306_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Orden_7306])
def read_orden_7306_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de orden_7306"""
    return orden_7306_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Orden_7306)
def read_orden_7306(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener orden_7306 por id"""
    db_obj = orden_7306_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Orden_7306 no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Orden_7306)
def update_orden_7306(
    id: int,
    obj_in: Orden_7306Update,
    db: Session = Depends(get_db)
):
    """Actualizar orden_7306"""
    db_obj = orden_7306_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Orden_7306 no encontrado"
        )
    return orden_7306_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_orden_7306(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar orden_7306"""
    success = orden_7306_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Orden_7306 no encontrado"
        )
