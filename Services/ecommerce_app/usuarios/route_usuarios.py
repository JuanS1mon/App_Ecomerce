# ============================================================================
# ROUTER: USUARIOS
# ============================================================================
"""
Router FastAPI para usuarios
Parte del servicio: ecommerce_app
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_usuarios import usuarios_service
from .schema_usuarios import Usuarios, UsuariosCreate, UsuariosUpdate

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Usuarios, status_code=status.HTTP_201_CREATED)
def create_usuarios(
    obj_in: UsuariosCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo usuarios"""
    return usuarios_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Usuarios])
def read_usuarios_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de usuarios"""
    return usuarios_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Usuarios)
def read_usuarios(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener usuarios por id"""
    db_obj = usuarios_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuarios no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Usuarios)
def update_usuarios(
    id: int,
    obj_in: UsuariosUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar usuarios"""
    db_obj = usuarios_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuarios no encontrado"
        )
    return usuarios_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuarios(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar usuarios"""
    success = usuarios_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuarios no encontrado"
        )
