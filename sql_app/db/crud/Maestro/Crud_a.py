from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from db.models import A
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_a(db: Session, a: A) -> A:
    """
    Crea un nuevo registro de A en la base de datos.
    """
    try:
        db.add(a)
        db.commit()
        db.refresh(a)
        return a
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear A: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_a(db: Session, id: int) -> Optional[A]:
    """
    Obtiene un registro de A por su clave primaria.
    """
    try:
        record = db.query(A).filter(A.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="A no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener A: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_a(db: Session) -> List[A]:
    """
    Obtiene una lista de todos los registros de A.
    """
    try:
        records = db.query(A).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de A: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_a(db: Session, id: int) -> A:
    """
    Elimina un registro de A por su clave primaria.
    """
    try:
        record = db.query(A).filter(A.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="A no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar A: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_a(db: Session, id: int, a_data: dict) -> A:
    """
    Actualiza un registro de A por su clave primaria.
    """
    logger.info(f"Actualizando A con id = { id }")
    try:
        record = db.query(A).filter(A.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="A no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in a_data.items():
            if key != 'id':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar A: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

