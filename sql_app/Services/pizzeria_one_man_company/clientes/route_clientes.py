# ============================================================================
# ROUTER: CLIENTES
# ============================================================================
"""
Router FastAPI para clientes
Parte del servicio: pizzeria_one_man_company
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_clientes import clientes_service
from .schema_clientes import Clientes, ClientesCreate, ClientesUpdate

router = APIRouter(
    prefix="/clientes",
    tags=["clientes"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Clientes, status_code=status.HTTP_201_CREATED)
def create_clientes(
    obj_in: ClientesCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo clientes"""
    return clientes_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Clientes])
def read_clientes_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de clientes"""
    return clientes_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Clientes)
def read_clientes(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener clientes por id"""
    db_obj = clientes_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clientes no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Clientes)
def update_clientes(
    id: int,
    obj_in: ClientesUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar clientes"""
    db_obj = clientes_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clientes no encontrado"
        )
    return clientes_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_clientes(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar clientes"""
    success = clientes_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clientes no encontrado"
        )
