from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from .model_prueba2 import Prueba2
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_prueba2(db: Session, prueba2: Prueba2) -> Prueba2:
    """
    Crea un nuevo registro de Prueba2 en la base de datos.
    """
    try:
        db.add(prueba2)
        db.commit()
        db.refresh(prueba2)
        return prueba2
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Prueba2: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_prueba2(db: Session, id: int) -> Optional[Prueba2]:
    """
    Obtiene un registro de Prueba2 por su clave primaria.
    """
    try:
        record = db.query(Prueba2).filter(Prueba2.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prueba2 no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Prueba2: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_prueba2(db: Session) -> List[Prueba2]:
    """
    Obtiene una lista de todos los registros de Prueba2.
    """
    try:
        records = db.query(Prueba2).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Prueba2: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_prueba2(db: Session, id: int) -> Prueba2:
    """
    Elimina un registro de Prueba2 por su clave primaria.
    """
    try:
        record = db.query(Prueba2).filter(Prueba2.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prueba2 no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Prueba2: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_prueba2(db: Session, id: int, prueba2_data: dict) -> Prueba2:
    """
    Actualiza un registro de Prueba2 por su clave primaria.
    """
    logger.info(f"Actualizando Prueba2 con id = { id }")
    try:
        record = db.query(Prueba2).filter(Prueba2.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prueba2 no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in prueba2_data.items():
            if key != 'id':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Prueba2: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

