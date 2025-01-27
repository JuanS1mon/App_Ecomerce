from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from db.models.carga import Carga
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_carga(db: Session, carga: Carga) -> Carga:
    """
    Crea un nuevo registro de Carga en la base de datos.
    """
    try:
        db.add(carga)
        db.commit()
        db.refresh(carga)
        return carga
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Carga: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_carga(db: Session, nrosuceso: int) -> Optional[Carga]:
    """
    Obtiene un registro de Carga por su clave primaria.
    """
    try:
        record = db.query(Carga).filter(Carga.nrosuceso == nrosuceso).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carga no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Carga: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_carga(db: Session) -> List[Carga]:
    """
    Obtiene una lista de todos los registros de Carga.
    """
    try:
        records = db.query(Carga).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Carga: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_carga(db: Session, nrosuceso: int) -> Carga:
    """
    Elimina un registro de Carga por su clave primaria.
    """
    try:
        record = db.query(Carga).filter(Carga.nrosuceso == nrosuceso).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carga no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Carga: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_carga(db: Session, nrosuceso: int, carga_data: dict) -> Carga:
    """
    Actualiza un registro de Carga por su clave primaria.
    """
    logger.info(f"Actualizando Carga con nrosuceso = { nrosuceso }")
    try:
        record = db.query(Carga).filter(Carga.nrosuceso == nrosuceso).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carga no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in carga_data.items():
            if key != 'nrosuceso':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Carga: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

