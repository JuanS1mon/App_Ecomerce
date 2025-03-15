from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from db.models.articulos import Articulos
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_articulos(db: Session, articulos: Articulos) -> Articulos:
    """
    Crea un nuevo registro de Articulos en la base de datos.
    """
    try:
        db.add(articulos)
        db.commit()
        db.refresh(articulos)
        return articulos
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_articulos(db: Session, id: int) -> Optional[Articulos]:
    """
    Obtiene un registro de Articulos por su clave primaria.
    """
    try:
        record = db.query(Articulos).filter(Articulos.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_articulos(db: Session) -> List[Articulos]:
    """
    Obtiene una lista de todos los registros de Articulos.
    """
    try:
        records = db.query(Articulos).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_articulos(db: Session, id: int) -> Articulos:
    """
    Elimina un registro de Articulos por su clave primaria.
    """
    try:
        record = db.query(Articulos).filter(Articulos.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_articulos(db: Session, id: int, articulos_data: dict) -> Articulos:
    """
    Actualiza un registro de Articulos por su clave primaria.
    """
    logger.info(f"Actualizando Articulos con id = { id }")
    try:
        record = db.query(Articulos).filter(Articulos.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in articulos_data.items():
            if key != 'id':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

