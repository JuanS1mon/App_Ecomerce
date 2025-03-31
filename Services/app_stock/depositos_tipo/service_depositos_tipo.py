from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from .model_depositos_tipo import Depositos_tipo
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_depositos_tipo(db: Session, depositos_tipo: Depositos_tipo) -> Depositos_tipo:
    """
    Crea un nuevo registro de Depositos_tipo en la base de datos.
    """
    try:
        db.add(depositos_tipo)
        db.commit()
        db.refresh(depositos_tipo)
        return depositos_tipo
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Depositos_tipo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_depositos_tipo(db: Session, id: int) -> Optional[Depositos_tipo]:
    """
    Obtiene un registro de Depositos_tipo por su clave primaria.
    """
    try:
        record = db.query(Depositos_tipo).filter(Depositos_tipo.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depositos_tipo no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Depositos_tipo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_depositos_tipo(db: Session) -> List[Depositos_tipo]:
    """
    Obtiene una lista de todos los registros de Depositos_tipo.
    """
    try:
        records = db.query(Depositos_tipo).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Depositos_tipo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_depositos_tipo(db: Session, id: int) -> Depositos_tipo:
    """
    Elimina un registro de Depositos_tipo por su clave primaria.
    """
    try:
        record = db.query(Depositos_tipo).filter(Depositos_tipo.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depositos_tipo no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Depositos_tipo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_depositos_tipo(db: Session, id: int, depositos_tipo_data: dict) -> Depositos_tipo:
    """
    Actualiza un registro de Depositos_tipo por su clave primaria.
    """
    logger.info(f"Actualizando Depositos_tipo con id = { id }")
    try:
        record = db.query(Depositos_tipo).filter(Depositos_tipo.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depositos_tipo no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in depositos_tipo_data.items():
            if key != 'id':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Depositos_tipo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

