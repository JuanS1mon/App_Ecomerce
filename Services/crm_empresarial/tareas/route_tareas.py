# ============================================================================
# ROUTER: TAREAS
# ============================================================================
"""
Router FastAPI para tareas
Parte del servicio: crm_empresarial
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_tareas import tareas_service
from .schema_tareas import Tareas, TareasCreate, TareasUpdate

router = APIRouter(
    prefix="/tareas",
    tags=["tareas"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Tareas, status_code=status.HTTP_201_CREATED)
def create_tareas(
    obj_in: TareasCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo tareas"""
    return tareas_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Tareas])
def read_tareas_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de tareas"""
    return tareas_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Tareas)
def read_tareas(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener tareas por id"""
    db_obj = tareas_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tareas no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Tareas)
def update_tareas(
    id: int,
    obj_in: TareasUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar tareas"""
    db_obj = tareas_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tareas no encontrado"
        )
    return tareas_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tareas(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar tareas"""
    success = tareas_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tareas no encontrado"
        )
