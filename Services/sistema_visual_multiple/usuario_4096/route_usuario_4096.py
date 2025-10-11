# ============================================================================
# ROUTER: USUARIO_4096
# ============================================================================
"""
Router FastAPI para usuario_4096
Parte del servicio: sistema_visual_multiple
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from .service_usuario_4096 import usuario_4096_service
from .schema_usuario_4096 import Usuario_4096, Usuario_4096Create, Usuario_4096Update

router = APIRouter(
    prefix="/usuario_4096",
    tags=["usuario_4096"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Usuario_4096, status_code=status.HTTP_201_CREATED)
def create_usuario_4096(
    obj_in: Usuario_4096Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo usuario_4096"""
    return usuario_4096_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Usuario_4096])
def read_usuario_4096_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de usuario_4096"""
    return usuario_4096_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Usuario_4096)
def read_usuario_4096(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener usuario_4096 por id"""
    db_obj = usuario_4096_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario_4096 no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Usuario_4096)
def update_usuario_4096(
    id: int,
    obj_in: Usuario_4096Update,
    db: Session = Depends(get_db)
):
    """Actualizar usuario_4096"""
    db_obj = usuario_4096_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario_4096 no encontrado"
        )
    return usuario_4096_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario_4096(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar usuario_4096"""
    success = usuario_4096_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario_4096 no encontrado"
        )
