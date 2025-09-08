# ============================================================================
# ROUTER: T
# ============================================================================
"""
Router FastAPI para t
Parte del servicio: test_service
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_t import t_service
from .schema_t import T, TCreate, TUpdate

router = APIRouter(
    prefix="/t",
    tags=["t"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=T, status_code=status.HTTP_201_CREATED)
def create_t(
    obj_in: TCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo t"""
    return t_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[T])
def read_t_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de t"""
    return t_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=T)
def read_t(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener t por id"""
    db_obj = t_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"T no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=T)
def update_t(
    id: int,
    obj_in: TUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar t"""
    db_obj = t_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"T no encontrado"
        )
    return t_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_t(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar t"""
    success = t_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"T no encontrado"
        )
