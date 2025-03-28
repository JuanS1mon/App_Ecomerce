from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from .model_facu_gay import Facu_gay
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_facu_gay(db: Session, facu_gay: Facu_gay) -> Facu_gay:
    """
    Crea un nuevo registro de Facu_gay en la base de datos.
    """
    try:
        db.add(facu_gay)
        db.commit()
        db.refresh(facu_gay)
        return facu_gay
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Facu_gay: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_facu_gay(db: Session, id: int) -> Optional[Facu_gay]:
    """
    Obtiene un registro de Facu_gay por su clave primaria.
    """
    try:
        record = db.query(Facu_gay).filter(Facu_gay.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facu_gay no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Facu_gay: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_facu_gay(db: Session) -> List[Facu_gay]:
    """
    Obtiene una lista de todos los registros de Facu_gay.
    """
    try:
        records = db.query(Facu_gay).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Facu_gay: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_facu_gay(db: Session, id: int) -> Facu_gay:
    """
    Elimina un registro de Facu_gay por su clave primaria.
    """
    try:
        record = db.query(Facu_gay).filter(Facu_gay.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facu_gay no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Facu_gay: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_facu_gay(db: Session, id: int, facu_gay_data: dict) -> Facu_gay:
    """
    Actualiza un registro de Facu_gay por su clave primaria.
    """
    logger.info(f"Actualizando Facu_gay con id = { id }")
    try:
        record = db.query(Facu_gay).filter(Facu_gay.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facu_gay no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in facu_gay_data.items():
            if key != 'id':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Facu_gay: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

