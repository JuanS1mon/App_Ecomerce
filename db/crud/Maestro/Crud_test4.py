from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from db.models.test4 import Test4
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_test4(db: Session, test4: Test4) -> Test4:
    """
    Crea un nuevo registro de Test4 en la base de datos.
    """
    try:
        db.add(test4)
        db.commit()
        db.refresh(test4)
        return test4
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Test4: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_test4(db: Session, codigo: int) -> Optional[Test4]:
    """
    Obtiene un registro de Test4 por su clave primaria.
    """
    try:
        record = db.query(Test4).filter(Test4.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test4 no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Test4: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_test4(db: Session) -> List[Test4]:
    """
    Obtiene una lista de todos los registros de Test4.
    """
    try:
        records = db.query(Test4).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Test4: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_test4(db: Session, codigo: int) -> Test4:
    """
    Elimina un registro de Test4 por su clave primaria.
    """
    try:
        record = db.query(Test4).filter(Test4.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test4 no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Test4: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_test4(db: Session, codigo: int, test4_data: dict) -> Test4:
    """
    Actualiza un registro de Test4 por su clave primaria.
    """
    logger.info(f"Actualizando Test4 con codigo = { codigo }")
    try:
        record = db.query(Test4).filter(Test4.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test4 no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in test4_data.items():
            if key != 'codigo':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Test4: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

