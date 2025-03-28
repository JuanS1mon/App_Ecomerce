from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from .model_test1 import Test1
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_test1(db: Session, test1: Test1) -> Test1:
    """
    Crea un nuevo registro de Test1 en la base de datos.
    """
    try:
        db.add(test1)
        db.commit()
        db.refresh(test1)
        return test1
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Test1: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_test1(db: Session, id: str) -> Optional[Test1]:
    """
    Obtiene un registro de Test1 por su clave primaria.
    """
    try:
        record = db.query(Test1).filter(Test1.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test1 no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Test1: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_test1(db: Session) -> List[Test1]:
    """
    Obtiene una lista de todos los registros de Test1.
    """
    try:
        records = db.query(Test1).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Test1: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_test1(db: Session, id: str) -> Test1:
    """
    Elimina un registro de Test1 por su clave primaria.
    """
    try:
        record = db.query(Test1).filter(Test1.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test1 no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Test1: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_test1(db: Session, id: str, test1_data: dict) -> Test1:
    """
    Actualiza un registro de Test1 por su clave primaria.
    """
    logger.info(f"Actualizando Test1 con id = { id }")
    try:
        record = db.query(Test1).filter(Test1.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test1 no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in test1_data.items():
            if key != 'id':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Test1: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

