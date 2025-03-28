from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from .model_prueba import Prueba
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_prueba(db: Session, prueba: Prueba) -> Prueba:
    """
    Crea un nuevo registro de Prueba en la base de datos.
    """
    try:
        db.add(prueba)
        db.commit()
        db.refresh(prueba)
        return prueba
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Prueba: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_prueba(db: Session, id: int) -> Optional[Prueba]:
    """
    Obtiene un registro de Prueba por su clave primaria.
    """
    try:
        record = db.query(Prueba).filter(Prueba.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prueba no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Prueba: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_prueba(db: Session) -> List[Prueba]:
    """
    Obtiene una lista de todos los registros de Prueba.
    """
    try:
        records = db.query(Prueba).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Prueba: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_prueba(db: Session, id: int) -> Prueba:
    """
    Elimina un registro de Prueba por su clave primaria.
    """
    try:
        record = db.query(Prueba).filter(Prueba.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prueba no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Prueba: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_prueba(db: Session, id: int, prueba_data: dict) -> Prueba:
    """
    Actualiza un registro de Prueba por su clave primaria.
    """
    logger.info(f"Actualizando Prueba con id = { id }")
    try:
        record = db.query(Prueba).filter(Prueba.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prueba no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in prueba_data.items():
            if key != 'id':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Prueba: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

