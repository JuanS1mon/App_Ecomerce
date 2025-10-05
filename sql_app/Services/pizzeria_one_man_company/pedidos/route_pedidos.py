# ============================================================================
# ROUTER: PEDIDOS
# ============================================================================
"""
Router FastAPI para pedidos
Parte del servicio: pizzeria_one_man_company
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_pedidos import pedidos_service
from .schema_pedidos import Pedidos, PedidosCreate, PedidosUpdate

router = APIRouter(
    prefix="/pedidos",
    tags=["pedidos"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Pedidos, status_code=status.HTTP_201_CREATED)
def create_pedidos(
    obj_in: PedidosCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo pedidos"""
    return pedidos_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Pedidos])
def read_pedidos_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de pedidos"""
    return pedidos_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Pedidos)
def read_pedidos(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener pedidos por id"""
    db_obj = pedidos_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedidos no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Pedidos)
def update_pedidos(
    id: int,
    obj_in: PedidosUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar pedidos"""
    db_obj = pedidos_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedidos no encontrado"
        )
    return pedidos_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pedidos(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar pedidos"""
    success = pedidos_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedidos no encontrado"
        )
