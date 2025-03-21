from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from db.models.planilla_test import Planilla_test
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_planilla_test(db: Session, planilla_test: Planilla_test) -> Planilla_test:
    """
    Crea un nuevo registro de Planilla_test en la base de datos.
    """
    try:
        db.add(planilla_test)
        db.commit()
        db.refresh(planilla_test)
        return planilla_test
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Planilla_test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_planilla_test(db: Session, codigo: int) -> Optional[Planilla_test]:
    """
    Obtiene un registro de Planilla_test por su clave primaria.
    """
    try:
        record = db.query(Planilla_test).filter(Planilla_test.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Planilla_test no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Planilla_test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_planilla_test(db: Session) -> List[Planilla_test]:
    """
    Obtiene una lista de todos los registros de Planilla_test.
    """
    try:
        records = db.query(Planilla_test).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Planilla_test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_planilla_test(db: Session, codigo: int) -> Planilla_test:
    """
    Elimina un registro de Planilla_test por su clave primaria.
    """
    try:
        record = db.query(Planilla_test).filter(Planilla_test.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Planilla_test no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Planilla_test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_planilla_test(db: Session, codigo: int, planilla_test_data: dict) -> Planilla_test:
    """
    Actualiza un registro de Planilla_test por su clave primaria.
    """
    logger.info(f"Actualizando Planilla_test con codigo = { codigo }")
    try:
        record = db.query(Planilla_test).filter(Planilla_test.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Planilla_test no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in planilla_test_data.items():
            if key != 'codigo':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Planilla_test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

