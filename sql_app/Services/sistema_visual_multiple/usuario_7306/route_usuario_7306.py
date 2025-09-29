# ============================================================================
# ROUTER: USUARIO_7306
# ============================================================================
"""
Router FastAPI para usuario_7306
Parte del servicio: sistema_visual_multiple
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_usuario_7306 import usuario_7306_service
from .schema_usuario_7306 import Usuario_7306, Usuario_7306Create, Usuario_7306Update

router = APIRouter(
    prefix="/usuario_7306",
    tags=["usuario_7306"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Usuario_7306, status_code=status.HTTP_201_CREATED)
def create_usuario_7306(
    obj_in: Usuario_7306Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo usuario_7306"""
    return usuario_7306_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Usuario_7306])
def read_usuario_7306_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de usuario_7306"""
    return usuario_7306_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Usuario_7306)
def read_usuario_7306(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener usuario_7306 por id"""
    db_obj = usuario_7306_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario_7306 no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Usuario_7306)
def update_usuario_7306(
    id: int,
    obj_in: Usuario_7306Update,
    db: Session = Depends(get_db)
):
    """Actualizar usuario_7306"""
    db_obj = usuario_7306_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario_7306 no encontrado"
        )
    return usuario_7306_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario_7306(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar usuario_7306"""
    success = usuario_7306_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario_7306 no encontrado"
        )
