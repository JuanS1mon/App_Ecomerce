# Imports de terceros
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import date

# Imports del proyecto
from .model_exhibitions import Exhibitions
from .schema_exhibitions import ExhibitionsCreate, ExhibitionsUpdate

import logging

logger = logging.getLogger(__name__)

def create_exhibitions(db: Session, exhibitions: Exhibitions):
    """Crear una nueva exhibición"""
    try:
        db.add(exhibitions)
        db.commit()
        db.refresh(exhibitions)
        return exhibitions
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear exhibición: {e}")
        raise e

def get_exhibitions(db: Session, exhibitions_id: int):
    """Obtener una exhibición por ID"""
    try:
        return db.query(Exhibitions).filter(Exhibitions.id == exhibitions_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener exhibición: {e}")
        raise e

def get_all_exhibitions(db: Session, skip: int = 0, limit: int = 100):
    """Obtener todas las exhibiciones con paginación"""
    try:
        return db.query(Exhibitions).order_by(Exhibitions.id.desc()).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener lista de exhibiciones: {e}")
        raise e

def get_exhibitions_by_artwork(db: Session, artwork_id: int):
    """Obtener exhibiciones por obra de arte"""
    try:
        return db.query(Exhibitions).filter(Exhibitions.artwork_id == artwork_id).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener exhibiciones por obra: {e}")
        raise e

def get_exhibitions_by_institution(db: Session, institution_id: int):
    """Obtener exhibiciones por institución"""
    try:
        return db.query(Exhibitions).filter(Exhibitions.institution_id == institution_id).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener exhibiciones por institución: {e}")
        raise e

def get_current_exhibitions(db: Session, current_date: date = None):
    """Obtener exhibiciones actuales (en curso)"""
    if current_date is None:
        current_date = date.today()
    try:
        return db.query(Exhibitions).filter(
            Exhibitions.start_date <= current_date,
            Exhibitions.end_date >= current_date
        ).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener exhibiciones actuales: {e}")
        raise e

def update_exhibitions(db: Session, exhibitions_id: int, exhibitions_update: ExhibitionsUpdate):
    """Actualizar una exhibición"""
    try:
        db_exhibitions = db.query(Exhibitions).filter(Exhibitions.id == exhibitions_id).first()
        if not db_exhibitions:
            return None
        
        update_data = exhibitions_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_exhibitions, field, value)
        
        db.commit()
        db.refresh(db_exhibitions)
        return db_exhibitions
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar exhibición: {e}")
        raise e

def delete_exhibitions(db: Session, exhibitions_id: int):
    """Eliminar una exhibición"""
    try:
        db_exhibitions = db.query(Exhibitions).filter(Exhibitions.id == exhibitions_id).first()
        if not db_exhibitions:
            return False
        
        db.delete(db_exhibitions)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar exhibición: {e}")
        raise e

def search_exhibitions_by_name(db: Session, name: str):
    """Buscar exhibiciones por nombre"""
    try:
        return db.query(Exhibitions).filter(Exhibitions.name.ilike(f"%{name}%")).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al buscar exhibiciones por nombre: {e}")
        raise e
