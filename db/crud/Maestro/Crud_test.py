from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from db.models.test import Test
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_test(db: Session, test: Test) -> Test:
    """
    Crea un nuevo registro de Test en la base de datos.
    """
    try:
        db.add(test)
        db.commit()
        db.refresh(test)
        return test
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_test(db: Session, codigo: int) -> Optional[Test]:
    """
    Obtiene un registro de Test por su clave primaria.
    """
    try:
        record = db.query(Test).filter(Test.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_test(db: Session) -> List[Test]:
    """
    Obtiene una lista de todos los registros de Test.
    """
    try:
        records = db.query(Test).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_test(db: Session, codigo: int) -> Test:
    """
    Elimina un registro de Test por su clave primaria.
    """
    try:
        record = db.query(Test).filter(Test.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_test(db: Session, codigo: int, test_data: dict) -> Test:
    """
    Actualiza un registro de Test por su clave primaria.
    """
    logger.info(f"Actualizando Test con codigo = { codigo }")
    try:
        record = db.query(Test).filter(Test.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in test_data.items():
            if key != 'codigo':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

