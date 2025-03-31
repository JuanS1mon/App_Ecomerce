from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from .model_stock_historico import Stock_historico
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_stock_historico(db: Session, stock_historico: Stock_historico) -> Stock_historico:
    """
    Crea un nuevo registro de Stock_historico en la base de datos.
    """
    try:
        db.add(stock_historico)
        db.commit()
        db.refresh(stock_historico)
        return stock_historico
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Stock_historico: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_stock_historico(db: Session, id: int) -> Optional[Stock_historico]:
    """
    Obtiene un registro de Stock_historico por su clave primaria.
    """
    try:
        record = db.query(Stock_historico).filter(Stock_historico.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock_historico no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Stock_historico: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_stock_historico(db: Session) -> List[Stock_historico]:
    """
    Obtiene una lista de todos los registros de Stock_historico.
    """
    try:
        records = db.query(Stock_historico).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Stock_historico: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_stock_historico(db: Session, id: int) -> Stock_historico:
    """
    Elimina un registro de Stock_historico por su clave primaria.
    """
    try:
        record = db.query(Stock_historico).filter(Stock_historico.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock_historico no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Stock_historico: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_stock_historico(db: Session, id: int, stock_historico_data: dict) -> Stock_historico:
    """
    Actualiza un registro de Stock_historico por su clave primaria.
    """
    logger.info(f"Actualizando Stock_historico con id = { id }")
    try:
        record = db.query(Stock_historico).filter(Stock_historico.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock_historico no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in stock_historico_data.items():
            if key != 'id':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Stock_historico: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

