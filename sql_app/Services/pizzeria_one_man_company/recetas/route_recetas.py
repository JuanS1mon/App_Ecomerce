# ============================================================================
# ROUTER: RECETAS
# ============================================================================
"""
Router FastAPI para recetas
Parte del servicio: pizzeria_one_man_company
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_recetas import recetas_service
from .schema_recetas import Recetas, RecetasCreate, RecetasUpdate

router = APIRouter(
    prefix="/recetas",
    tags=["recetas"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Recetas, status_code=status.HTTP_201_CREATED)
def create_recetas(
    obj_in: RecetasCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo recetas"""
    return recetas_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Recetas])
def read_recetas_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de recetas"""
    return recetas_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Recetas)
def read_recetas(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener recetas por id"""
    db_obj = recetas_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recetas no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Recetas)
def update_recetas(
    id: int,
    obj_in: RecetasUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar recetas"""
    db_obj = recetas_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recetas no encontrado"
        )
    return recetas_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recetas(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar recetas"""
    success = recetas_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recetas no encontrado"
        )
