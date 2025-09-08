# ============================================================================
# ROUTER: USUARIO_2650
# ============================================================================
"""
Router FastAPI para usuario_2650
Parte del servicio: dm3
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_usuario_2650 import usuario_2650_service
from .schema_usuario_2650 import Usuario_2650, Usuario_2650Create, Usuario_2650Update

router = APIRouter(
    prefix="/usuario_2650",
    tags=["usuario_2650"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Usuario_2650, status_code=status.HTTP_201_CREATED)
def create_usuario_2650(
    obj_in: Usuario_2650Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo usuario_2650"""
    return usuario_2650_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Usuario_2650])
def read_usuario_2650_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de usuario_2650"""
    return usuario_2650_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Usuario_2650)
def read_usuario_2650(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener usuario_2650 por id"""
    db_obj = usuario_2650_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario_2650 no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Usuario_2650)
def update_usuario_2650(
    id: int,
    obj_in: Usuario_2650Update,
    db: Session = Depends(get_db)
):
    """Actualizar usuario_2650"""
    db_obj = usuario_2650_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario_2650 no encontrado"
        )
    return usuario_2650_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario_2650(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar usuario_2650"""
    success = usuario_2650_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario_2650 no encontrado"
        )
