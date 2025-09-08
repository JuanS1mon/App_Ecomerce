# ============================================================================
# ROUTER: CATEGORIA_4096
# ============================================================================
"""
Router FastAPI para categoria_4096
Parte del servicio: sistema_visual_multiple
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_categoria_4096 import categoria_4096_service
from .schema_categoria_4096 import Categoria_4096, Categoria_4096Create, Categoria_4096Update

router = APIRouter(
    prefix="/categoria_4096",
    tags=["categoria_4096"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Categoria_4096, status_code=status.HTTP_201_CREATED)
def create_categoria_4096(
    obj_in: Categoria_4096Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo categoria_4096"""
    return categoria_4096_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Categoria_4096])
def read_categoria_4096_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de categoria_4096"""
    return categoria_4096_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Categoria_4096)
def read_categoria_4096(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener categoria_4096 por id"""
    db_obj = categoria_4096_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria_4096 no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Categoria_4096)
def update_categoria_4096(
    id: int,
    obj_in: Categoria_4096Update,
    db: Session = Depends(get_db)
):
    """Actualizar categoria_4096"""
    db_obj = categoria_4096_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria_4096 no encontrado"
        )
    return categoria_4096_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_categoria_4096(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar categoria_4096"""
    success = categoria_4096_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria_4096 no encontrado"
        )
