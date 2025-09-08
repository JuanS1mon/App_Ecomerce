# ============================================================================
# ROUTER: USUARIO_5372
# ============================================================================
"""
Router FastAPI para usuario_5372
Parte del servicio: sistema_visual_multiple
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_usuario_5372 import usuario_5372_service
from .schema_usuario_5372 import Usuario_5372, Usuario_5372Create, Usuario_5372Update

router = APIRouter(
    prefix="/usuario_5372",
    tags=["usuario_5372"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Usuario_5372, status_code=status.HTTP_201_CREATED)
def create_usuario_5372(
    obj_in: Usuario_5372Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo usuario_5372"""
    return usuario_5372_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Usuario_5372])
def read_usuario_5372_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de usuario_5372"""
    return usuario_5372_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Usuario_5372)
def read_usuario_5372(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener usuario_5372 por id"""
    db_obj = usuario_5372_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario_5372 no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Usuario_5372)
def update_usuario_5372(
    id: int,
    obj_in: Usuario_5372Update,
    db: Session = Depends(get_db)
):
    """Actualizar usuario_5372"""
    db_obj = usuario_5372_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario_5372 no encontrado"
        )
    return usuario_5372_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario_5372(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar usuario_5372"""
    success = usuario_5372_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario_5372 no encontrado"
        )
