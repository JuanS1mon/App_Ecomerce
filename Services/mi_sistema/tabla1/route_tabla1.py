# ============================================================================
# ROUTER: TABLA1
# ============================================================================
"""
Router FastAPI para tabla1
Parte del servicio: mi_sistema
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from .service_tabla1 import tabla1_service
from .schema_tabla1 import Tabla1, Tabla1Create, Tabla1Update

router = APIRouter(
    prefix="/tabla1",
    tags=["tabla1"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Tabla1, status_code=status.HTTP_201_CREATED)
def create_tabla1(
    obj_in: Tabla1Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo tabla1"""
    return tabla1_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Tabla1])
def read_tabla1_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de tabla1"""
    return tabla1_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Tabla1)
def read_tabla1(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener tabla1 por id"""
    db_obj = tabla1_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tabla1 no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Tabla1)
def update_tabla1(
    id: int,
    obj_in: Tabla1Update,
    db: Session = Depends(get_db)
):
    """Actualizar tabla1"""
    db_obj = tabla1_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tabla1 no encontrado"
        )
    return tabla1_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tabla1(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar tabla1"""
    success = tabla1_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tabla1 no encontrado"
        )
