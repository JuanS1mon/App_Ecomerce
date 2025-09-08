# Imports de terceros
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Imports del proyecto
from .model_institutions import Institutions
from .schema_institutions import InstitutionsCreate, InstitutionsUpdate

import logging

logger = logging.getLogger(__name__)

def create_institutions(db: Session, institutions: Institutions):
    """Crear una nueva institución"""
    try:
        db.add(institutions)
        db.commit()
        db.refresh(institutions)
        return institutions
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear institución: {e}")
        raise e

def get_institutions(db: Session, institutions_id: int):
    """Obtener una institución por ID"""
    try:
        return db.query(Institutions).filter(Institutions.id == institutions_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener institución: {e}")
        raise e

def get_all_institutions(db: Session, skip: int = 0, limit: int = 100):
    """Obtener todas las instituciones con paginación"""
    try:
        return db.query(Institutions).order_by(Institutions.id.desc()).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener lista de instituciones: {e}")
        raise e

def get_institutions_by_location(db: Session, location_id: int):
    """Obtener instituciones por ubicación"""
    try:
        return db.query(Institutions).filter(Institutions.location_id == location_id).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener instituciones por ubicación: {e}")
        raise e

def update_institutions(db: Session, institutions_id: int, institutions_update: InstitutionsUpdate):
    """Actualizar una institución"""
    try:
        db_institutions = db.query(Institutions).filter(Institutions.id == institutions_id).first()
        if not db_institutions:
            return None
        
        update_data = institutions_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_institutions, field, value)
        
        db.commit()
        db.refresh(db_institutions)
        return db_institutions
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar institución: {e}")
        raise e

def delete_institutions(db: Session, institutions_id: int):
    """Eliminar una institución"""
    try:
        db_institutions = db.query(Institutions).filter(Institutions.id == institutions_id).first()
        if not db_institutions:
            return False
        
        db.delete(db_institutions)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar institución: {e}")
        raise e

def search_institutions_by_name(db: Session, name: str):
    """Buscar instituciones por nombre"""
    try:
        return db.query(Institutions).filter(Institutions.name.ilike(f"%{name}%")).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al buscar instituciones por nombre: {e}")
        raise e
