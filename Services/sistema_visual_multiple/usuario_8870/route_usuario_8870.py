# ============================================================================
# ROUTER: USUARIO_8870
# ============================================================================
"""
Router FastAPI para usuario_8870
Parte del servicio: sistema_visual_multiple
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_usuario_8870 import usuario_8870_service
from .schema_usuario_8870 import Usuario8870, Usuario8870Create, Usuario8870Update

router = APIRouter(
    prefix="/usuario_8870",
    tags=["usuario_8870"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Usuario8870, status_code=status.HTTP_201_CREATED)
def create_usuario_8870(
    obj_in: Usuario8870Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo usuario_8870"""
    return usuario_8870_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Usuario8870])
def read_usuario_8870_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de usuario_8870"""
    return usuario_8870_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Usuario8870)
def read_usuario_8870(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener usuario_8870 por id"""
    db_obj = usuario_8870_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario8870 no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Usuario8870)
def update_usuario_8870(
    id: int,
    obj_in: Usuario8870Update,
    db: Session = Depends(get_db)
):
    """Actualizar usuario_8870"""
    db_obj = usuario_8870_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario8870 no encontrado"
        )
    return usuario_8870_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario_8870(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar usuario_8870"""
    success = usuario_8870_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario8870 no encontrado"
        )
