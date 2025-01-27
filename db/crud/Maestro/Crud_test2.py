from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from db.models.test2 import Test2
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_test2(db: Session, test2: Test2) -> Test2:
    """
    Crea un nuevo registro de Test2 en la base de datos.
    """
    try:
        db.add(test2)
        db.commit()
        db.refresh(test2)
        return test2
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Test2: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_test2(db: Session, codigo: int) -> Optional[Test2]:
    """
    Obtiene un registro de Test2 por su clave primaria.
    """
    try:
        record = db.query(Test2).filter(Test2.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test2 no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Test2: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_test2(db: Session) -> List[Test2]:
    """
    Obtiene una lista de todos los registros de Test2.
    """
    try:
        records = db.query(Test2).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Test2: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_test2(db: Session, codigo: int) -> Test2:
    """
    Elimina un registro de Test2 por su clave primaria.
    """
    try:
        record = db.query(Test2).filter(Test2.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test2 no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Test2: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_test2(db: Session, codigo: int, test2_data: dict) -> Test2:
    """
    Actualiza un registro de Test2 por su clave primaria.
    """
    logger.info(f"Actualizando Test2 con codigo = { codigo }")
    try:
        record = db.query(Test2).filter(Test2.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test2 no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in test2_data.items():
            if key != 'codigo':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Test2: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

