from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from db.models.familias import Familias
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_familias(db: Session, familias: Familias) -> Familias:
    """
    Crea un nuevo registro de Familias en la base de datos.
    """
    try:
        db.add(familias)
        db.commit()
        db.refresh(familias)
        return familias
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Familias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_familias(db: Session, codigo: int) -> Optional[Familias]:
    """
    Obtiene un registro de Familias por su clave primaria.
    """
    try:
        record = db.query(Familias).filter(Familias.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Familias no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Familias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_familias(db: Session) -> List[Familias]:
    """
    Obtiene una lista de todos los registros de Familias.
    """
    try:
        records = db.query(Familias).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Familias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_familias(db: Session, codigo: int) -> Familias:
    """
    Elimina un registro de Familias por su clave primaria.
    """
    try:
        record = db.query(Familias).filter(Familias.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Familias no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Familias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_familias(db: Session, codigo: int, familias_data: dict) -> Familias:
    """
    Actualiza un registro de Familias por su clave primaria.
    """
    logger.info(f"Actualizando Familias con codigo = { codigo }")
    try:
        record = db.query(Familias).filter(Familias.codigo == codigo).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Familias no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in familias_data.items():
            if key != 'codigo':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Familias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

