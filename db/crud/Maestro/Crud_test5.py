from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from db.models.test5 import Test5
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_test5(db: Session, test5: Test5) -> Test5:
    """
    Crea un nuevo registro de Test5 en la base de datos.
    """
    try:
        db.add(test5)
        db.commit()
        db.refresh(test5)
        return test5
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Test5: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_test5(db: Session, codigo: int) -> Optional[Test5]:
    """
    Obtiene un registro de Test5 por su clave primaria.
    """
    try:
        record = db.query(Test5).filter(Test5.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test5 no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Test5: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_test5(db: Session) -> List[Test5]:
    """
    Obtiene una lista de todos los registros de Test5.
    """
    try:
        records = db.query(Test5).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Test5: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_test5(db: Session, codigo: int) -> Test5:
    """
    Elimina un registro de Test5 por su clave primaria.
    """
    try:
        record = db.query(Test5).filter(Test5.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test5 no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Test5: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_test5(db: Session, codigo: int, test5_data: dict) -> Test5:
    """
    Actualiza un registro de Test5 por su clave primaria.
    """
    logger.info(f"Actualizando Test5 con codigo = { codigo }")
    try:
        record = db.query(Test5).filter(Test5.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test5 no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in test5_data.items():
            if key != 'codigo':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Test5: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

