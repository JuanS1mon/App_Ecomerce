# ============================================================================
# ROUTER: ORDENES
# ============================================================================
"""
Router FastAPI para ordenes
Parte del servicio: ecommerce_app
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_ordenes import ordenes_service
from .schema_ordenes import Ordenes, OrdenesCreate, OrdenesUpdate

router = APIRouter(
    prefix="/ordenes",
    tags=["ordenes"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Ordenes, status_code=status.HTTP_201_CREATED)
def create_ordenes(
    obj_in: OrdenesCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo ordenes"""
    return ordenes_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Ordenes])
def read_ordenes_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de ordenes"""
    return ordenes_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Ordenes)
def read_ordenes(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener ordenes por id"""
    db_obj = ordenes_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ordenes no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Ordenes)
def update_ordenes(
    id: int,
    obj_in: OrdenesUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar ordenes"""
    db_obj = ordenes_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ordenes no encontrado"
        )
    return ordenes_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ordenes(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar ordenes"""
    success = ordenes_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ordenes no encontrado"
        )
