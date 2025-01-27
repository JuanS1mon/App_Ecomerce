from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from db.models.test3 import Test3
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_test3(db: Session, test3: Test3) -> Test3:
    """
    Crea un nuevo registro de Test3 en la base de datos.
    """
    try:
        db.add(test3)
        db.commit()
        db.refresh(test3)
        return test3
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Test3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_test3(db: Session, codigo: int) -> Optional[Test3]:
    """
    Obtiene un registro de Test3 por su clave primaria.
    """
    try:
        record = db.query(Test3).filter(Test3.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test3 no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Test3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_test3(db: Session) -> List[Test3]:
    """
    Obtiene una lista de todos los registros de Test3.
    """
    try:
        records = db.query(Test3).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Test3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_test3(db: Session, codigo: int) -> Test3:
    """
    Elimina un registro de Test3 por su clave primaria.
    """
    try:
        record = db.query(Test3).filter(Test3.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test3 no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Test3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_test3(db: Session, codigo: int, test3_data: dict) -> Test3:
    """
    Actualiza un registro de Test3 por su clave primaria.
    """
    logger.info(f"Actualizando Test3 con codigo = { codigo }")
    try:
        record = db.query(Test3).filter(Test3.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test3 no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in test3_data.items():
            if key != 'codigo':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Test3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

