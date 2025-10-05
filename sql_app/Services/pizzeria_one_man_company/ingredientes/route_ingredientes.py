# ============================================================================
# ROUTER: INGREDIENTES
# ============================================================================
"""
Router FastAPI para ingredientes
Parte del servicio: pizzeria_one_man_company
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_ingredientes import ingredientes_service
from .schema_ingredientes import Ingredientes, IngredientesCreate, IngredientesUpdate

router = APIRouter(
    prefix="/ingredientes",
    tags=["ingredientes"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Ingredientes, status_code=status.HTTP_201_CREATED)
def create_ingredientes(
    obj_in: IngredientesCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo ingredientes"""
    return ingredientes_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Ingredientes])
def read_ingredientes_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de ingredientes"""
    return ingredientes_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Ingredientes)
def read_ingredientes(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener ingredientes por id"""
    db_obj = ingredientes_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredientes no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Ingredientes)
def update_ingredientes(
    id: int,
    obj_in: IngredientesUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar ingredientes"""
    db_obj = ingredientes_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredientes no encontrado"
        )
    return ingredientes_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredientes(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar ingredientes"""
    success = ingredientes_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredientes no encontrado"
        )
