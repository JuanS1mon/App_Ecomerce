from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from .model_stock_current import Stock_current
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_stock_current(db: Session, stock_current: Stock_current) -> Stock_current:
    """
    Crea un nuevo registro de Stock_current en la base de datos.
    """
    try:
        db.add(stock_current)
        db.commit()
        db.refresh(stock_current)
        return stock_current
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Stock_current: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_stock_current(db: Session, id: int) -> Optional[Stock_current]:
    """
    Obtiene un registro de Stock_current por su clave primaria.
    """
    try:
        record = db.query(Stock_current).filter(Stock_current.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock_current no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Stock_current: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_stock_current(db: Session) -> List[Stock_current]:
    """
    Obtiene una lista de todos los registros de Stock_current.
    """
    try:
        records = db.query(Stock_current).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Stock_current: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_stock_current(db: Session, id: int) -> Stock_current:
    """
    Elimina un registro de Stock_current por su clave primaria.
    """
    try:
        record = db.query(Stock_current).filter(Stock_current.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock_current no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Stock_current: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_stock_current(db: Session, id: int, stock_current_data: dict) -> Stock_current:
    """
    Actualiza un registro de Stock_current por su clave primaria.
    """
    logger.info(f"Actualizando Stock_current con id = { id }")
    try:
        record = db.query(Stock_current).filter(Stock_current.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock_current no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in stock_current_data.items():
            if key != 'id':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Stock_current: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

