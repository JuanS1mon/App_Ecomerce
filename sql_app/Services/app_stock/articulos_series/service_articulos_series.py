from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from .model_articulos_series import Articulos_series
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_articulos_series(db: Session, articulos_series: Articulos_series) -> Articulos_series:
    """
    Crea un nuevo registro de Articulos_series en la base de datos.
    """
    try:
        db.add(articulos_series)
        db.commit()
        db.refresh(articulos_series)
        return articulos_series
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Articulos_series: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_articulos_series(db: Session, id: int) -> Optional[Articulos_series]:
    """
    Obtiene un registro de Articulos_series por su clave primaria.
    """
    try:
        record = db.query(Articulos_series).filter(Articulos_series.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos_series no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Articulos_series: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_articulos_series(db: Session) -> List[Articulos_series]:
    """
    Obtiene una lista de todos los registros de Articulos_series.
    """
    try:
        records = db.query(Articulos_series).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Articulos_series: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_articulos_series(db: Session, id: int) -> Articulos_series:
    """
    Elimina un registro de Articulos_series por su clave primaria.
    """
    try:
        record = db.query(Articulos_series).filter(Articulos_series.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos_series no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Articulos_series: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_articulos_series(db: Session, id: int, articulos_series_data: dict) -> Articulos_series:
    """
    Actualiza un registro de Articulos_series por su clave primaria.
    """
    logger.info(f"Actualizando Articulos_series con id = { id }")
    try:
        record = db.query(Articulos_series).filter(Articulos_series.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos_series no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in articulos_series_data.items():
            if key != 'id':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Articulos_series: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

