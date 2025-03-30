from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from .model_articulos_tipos import Articulos_tipos
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_articulos_tipos(db: Session, articulos_tipos: Articulos_tipos) -> Articulos_tipos:
    """
    Crea un nuevo registro de Articulos_tipos en la base de datos.
    """
    try:
        db.add(articulos_tipos)
        db.commit()
        db.refresh(articulos_tipos)
        return articulos_tipos
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Articulos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_articulos_tipos(db: Session, id: int) -> Optional[Articulos_tipos]:
    """
    Obtiene un registro de Articulos_tipos por su clave primaria.
    """
    try:
        record = db.query(Articulos_tipos).filter(Articulos_tipos.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos_tipos no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Articulos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_articulos_tipos(db: Session) -> List[Articulos_tipos]:
    """
    Obtiene una lista de todos los registros de Articulos_tipos.
    """
    try:
        records = db.query(Articulos_tipos).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Articulos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_articulos_tipos(db: Session, id: int) -> Articulos_tipos:
    """
    Elimina un registro de Articulos_tipos por su clave primaria.
    """
    try:
        record = db.query(Articulos_tipos).filter(Articulos_tipos.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos_tipos no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Articulos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_articulos_tipos(db: Session, id: int, articulos_tipos_data: dict) -> Articulos_tipos:
    """
    Actualiza un registro de Articulos_tipos por su clave primaria.
    """
    logger.info(f"Actualizando Articulos_tipos con id = { id }")
    try:
        record = db.query(Articulos_tipos).filter(Articulos_tipos.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos_tipos no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in articulos_tipos_data.items():
            if key != 'id':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Articulos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

