# ============================================================================
# ROUTER: OPORTUNIDADES
# ============================================================================
"""
Router FastAPI para oportunidades
Parte del servicio: crm_empresarial
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_oportunidades import oportunidades_service
from .schema_oportunidades import Oportunidades, OportunidadesCreate, OportunidadesUpdate

router = APIRouter(
    prefix="/oportunidades",
    tags=["oportunidades"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=Oportunidades, status_code=status.HTTP_201_CREATED)
def create_oportunidades(
    obj_in: OportunidadesCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo oportunidades"""
    return oportunidades_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[Oportunidades])
def read_oportunidades_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de oportunidades"""
    return oportunidades_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Oportunidades)
def read_oportunidades(
    id: int,
    db: Session = Depends(get_db)
):
    """Obtener oportunidades por id"""
    db_obj = oportunidades_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Oportunidades no encontrado"
        )
    return db_obj

@router.put("/{id}", response_model=Oportunidades)
def update_oportunidades(
    id: int,
    obj_in: OportunidadesUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar oportunidades"""
    db_obj = oportunidades_service.get(db=db, id=id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Oportunidades no encontrado"
        )
    return oportunidades_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_oportunidades(
    id: int,
    db: Session = Depends(get_db)
):
    """Eliminar oportunidades"""
    success = oportunidades_service.delete(db=db, id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Oportunidades no encontrado"
        )
