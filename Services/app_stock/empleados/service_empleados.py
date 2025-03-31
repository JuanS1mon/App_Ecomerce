from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from .model_empleados import Empleados
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_empleados(db: Session, empleados: Empleados) -> Empleados:
    """
    Crea un nuevo registro de Empleados en la base de datos.
    """
    try:
        db.add(empleados)
        db.commit()
        db.refresh(empleados)
        return empleados
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Empleados: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

def get_empleados(db: Session, id: int) -> Optional[Empleados]:
    """
    Obtiene un registro de Empleados por su clave primaria.
    """
    try:
        record = db.query(Empleados).filter(Empleados.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empleados no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Empleados: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

def gets_empleados(db: Session) -> List[Empleados]:
    """
    Obtiene una lista de todos los registros de Empleados.
    """
    try:
        records = db.query(Empleados).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Empleados: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

def delete_empleados(db: Session, id: int) -> Empleados:
    """
    Elimina un registro de Empleados por su clave primaria.
    """
    try:
        record = db.query(Empleados).filter(Empleados.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empleados no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Empleados: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

def update_empleados(db: Session, id: int, empleados_data: dict) -> Empleados:
    """
    Actualiza un registro de Empleados por su clave primaria.
    """
    logger.info(f"Actualizando Empleados con id = { id }")
    try:
        record = db.query(Empleados).filter(Empleados.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empleados no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in empleados_data.items():
            if key != 'id':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Empleados: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

