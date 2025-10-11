# ============================================================================
# ROUTER: AUTORES
# ============================================================================
"""
Router FastAPI para autores
Parte del servicio: biblioteca_sistema
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from .service_autores import autores_service
from .schema_autores import Autores, AutoresCreate, AutoresUpdate

router = APIRouter(
    prefix="/autores",
    tags=["autores"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Autores, status_code=status.HTTP_201_CREATED)
def create_autores(
    obj_in: AutoresCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo autores"""
    return autores_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Autores])
def read_autores_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de autores"""
    return autores_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Autores)
def read_autores(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener autores por id"""
    db_obj = autores_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Autores no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Autores)
def update_autores(
    id: int,
    obj_in: AutoresUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar autores"""
    db_obj = autores_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Autores no encontrado"
        )
    return autores_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_autores(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar autores"""
    success = autores_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Autores no encontrado"
        )
