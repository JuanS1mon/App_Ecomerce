from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from .model_prueba3 import Prueba3
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_prueba3(db: Session, prueba3: Prueba3) -> Prueba3:
    """
    Crea un nuevo registro de Prueba3 en la base de datos.
    """
    try:
        db.add(prueba3)
        db.commit()
        db.refresh(prueba3)
        return prueba3
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Prueba3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_prueba3(db: Session, id: int) -> Optional[Prueba3]:
    """
    Obtiene un registro de Prueba3 por su clave primaria.
    """
    try:
        record = db.query(Prueba3).filter(Prueba3.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prueba3 no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Prueba3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_prueba3(db: Session) -> List[Prueba3]:
    """
    Obtiene una lista de todos los registros de Prueba3.
    """
    try:
        records = db.query(Prueba3).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Prueba3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_prueba3(db: Session, id: int) -> Prueba3:
    """
    Elimina un registro de Prueba3 por su clave primaria.
    """
    try:
        record = db.query(Prueba3).filter(Prueba3.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prueba3 no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Prueba3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_prueba3(db: Session, id: int, prueba3_data: dict) -> Prueba3:
    """
    Actualiza un registro de Prueba3 por su clave primaria.
    """
    logger.info(f"Actualizando Prueba3 con id = { id }")
    try:
        record = db.query(Prueba3).filter(Prueba3.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prueba3 no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in prueba3_data.items():
            if key != 'id':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Prueba3: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

