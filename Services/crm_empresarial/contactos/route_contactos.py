# ============================================================================
# ROUTER: CONTACTOS
# ============================================================================
"""
Router FastAPI para contactos
Parte del servicio: crm_empresarial
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_contactos import contactos_service
from .schema_contactos import Contactos, ContactosCreate, ContactosUpdate

router = APIRouter(
    prefix="/contactos",
    tags=["contactos"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Contactos, status_code=status.HTTP_201_CREATED)
def create_contactos(
    obj_in: ContactosCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo contactos"""
    return contactos_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Contactos])
def read_contactos_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de contactos"""
    return contactos_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Contactos)
def read_contactos(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener contactos por id"""
    db_obj = contactos_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contactos no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Contactos)
def update_contactos(
    id: int,
    obj_in: ContactosUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar contactos"""
    db_obj = contactos_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contactos no encontrado"
        )
    return contactos_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contactos(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar contactos"""
    success = contactos_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contactos no encontrado"
        )
