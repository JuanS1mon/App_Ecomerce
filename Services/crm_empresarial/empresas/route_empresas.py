# ============================================================================
# ROUTER: EMPRESAS
# ============================================================================
"""
Router FastAPI para empresas
Parte del servicio: crm_empresarial
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_empresas import empresas_service
from .schema_empresas import Empresas, EmpresasCreate, EmpresasUpdate

router = APIRouter(
    prefix="/empresas",
    tags=["empresas"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Empresas, status_code=status.HTTP_201_CREATED)
def create_empresas(
    obj_in: EmpresasCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo empresas"""
    return empresas_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Empresas])
def read_empresas_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de empresas"""
    return empresas_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Empresas)
def read_empresas(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener empresas por id"""
    db_obj = empresas_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Empresas no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Empresas)
def update_empresas(
    id: int,
    obj_in: EmpresasUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar empresas"""
    db_obj = empresas_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Empresas no encontrado"
        )
    return empresas_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_empresas(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar empresas"""
    success = empresas_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Empresas no encontrado"
        )
