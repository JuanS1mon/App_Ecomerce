from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from .model_depositos import Depositos
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_depositos(db: Session, depositos: Depositos) -> Depositos:
    """
    Crea un nuevo registro de Depositos en la base de datos.
    """
    try:
        db.add(depositos)
        db.commit()
        db.refresh(depositos)
        return depositos
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Depositos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_depositos(db: Session, id: int) -> Optional[Depositos]:
    """
    Obtiene un registro de Depositos por su clave primaria.
    """
    try:
        record = db.query(Depositos).filter(Depositos.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depositos no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Depositos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_depositos(db: Session) -> List[Depositos]:
    """
    Obtiene una lista de todos los registros de Depositos.
    """
    try:
        records = db.query(Depositos).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Depositos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_depositos(db: Session, id: int) -> Depositos:
    """
    Elimina un registro de Depositos por su clave primaria.
    """
    try:
        record = db.query(Depositos).filter(Depositos.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depositos no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Depositos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_depositos(db: Session, id: int, depositos_data: dict) -> Depositos:
    """
    Actualiza un registro de Depositos por su clave primaria.
    """
    logger.info(f"Actualizando Depositos con id = { id }")
    try:
        record = db.query(Depositos).filter(Depositos.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depositos no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in depositos_data.items():
            if key != 'id':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Depositos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

