# ============================================================================
# ROUTER: USUARIO_5862
# ============================================================================
"""
Router FastAPI para usuario_5862
Parte del servicio: sistema_visual_multiple
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_usuario_5862 import usuario_5862_service
from .schema_usuario_5862 import Usuario_5862, Usuario_5862Create, Usuario_5862Update

router = APIRouter(
    prefix="/usuario_5862",
    tags=["usuario_5862"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Usuario_5862, status_code=status.HTTP_201_CREATED)
def create_usuario_5862(
    obj_in: Usuario_5862Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo usuario_5862"""
    return usuario_5862_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Usuario_5862])
def read_usuario_5862_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de usuario_5862"""
    return usuario_5862_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Usuario_5862)
def read_usuario_5862(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener usuario_5862 por id"""
    db_obj = usuario_5862_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario_5862 no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Usuario_5862)
def update_usuario_5862(
    id: int,
    obj_in: Usuario_5862Update,
    db: Session = Depends(get_db)
):
    """Actualizar usuario_5862"""
    db_obj = usuario_5862_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario_5862 no encontrado"
        )
    return usuario_5862_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario_5862(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar usuario_5862"""
    success = usuario_5862_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario_5862 no encontrado"
        )
