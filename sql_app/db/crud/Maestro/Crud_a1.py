from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from db.models.a1 import A1
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_a1(db: Session, a1: A1) -> A1:
    """
    Crea un nuevo registro de A1 en la base de datos.
    """
    try:
        db.add(a1)
        db.commit()
        db.refresh(a1)
        return a1
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear A1: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_a1(db: Session, a: int) -> Optional[A1]:
    """
    Obtiene un registro de A1 por su clave primaria.
    """
    try:
        record = db.query(A1).filter(A1.a == a).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="A1 no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener A1: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_a1(db: Session) -> List[A1]:
    """
    Obtiene una lista de todos los registros de A1.
    """
    try:
        records = db.query(A1).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de A1: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_a1(db: Session, a: int) -> A1:
    """
    Elimina un registro de A1 por su clave primaria.
    """
    try:
        record = db.query(A1).filter(A1.a == a).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="A1 no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar A1: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_a1(db: Session, a: int, a1_data: dict) -> A1:
    """
    Actualiza un registro de A1 por su clave primaria.
    """
    logger.info(f"Actualizando A1 con a = { a }")
    try:
        record = db.query(A1).filter(A1.a == a).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="A1 no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in a1_data.items():
            if key != 'a':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar A1: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

