# ============================================================================
# ROUTER: LIBROS
# ============================================================================
"""
Router FastAPI para libros
Parte del servicio: biblioteca_sistema
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from .service_libros import libros_service
from .schema_libros import Libros, LibrosCreate, LibrosUpdate

router = APIRouter(
    prefix="/libros",
    tags=["libros"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Libros, status_code=status.HTTP_201_CREATED)
def create_libros(
    obj_in: LibrosCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo libros"""
    return libros_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Libros])
def read_libros_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de libros"""
    return libros_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Libros)
def read_libros(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener libros por id"""
    db_obj = libros_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Libros no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Libros)
def update_libros(
    id: int,
    obj_in: LibrosUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar libros"""
    db_obj = libros_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Libros no encontrado"
        )
    return libros_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_libros(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar libros"""
    success = libros_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Libros no encontrado"
        )
