# Imports de terceros
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Imports del proyecto
from .model_locations import Locations
from .schema_locations import LocationsCreate, LocationsUpdate

import logging

logger = logging.getLogger(__name__)

def create_locations(db: Session, locations: Locations):
    """Crear una nueva ubicación"""
    try:
        db.add(locations)
        db.commit()
        db.refresh(locations)
        return locations
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear ubicación: {e}")
        raise e

def get_locations(db: Session, locations_id: int):
    """Obtener una ubicación por ID"""
    try:
        return db.query(Locations).filter(Locations.id == locations_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener ubicación: {e}")
        raise e

def get_all_locations(db: Session, skip: int = 0, limit: int = 100):
    """Obtener todas las ubicaciones con paginación"""
    try:
        return db.query(Locations).order_by(Locations.id.desc()).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener lista de ubicaciones: {e}")
        raise e

def update_locations(db: Session, locations_id: int, locations_update: LocationsUpdate):
    """Actualizar una ubicación"""
    try:
        db_locations = db.query(Locations).filter(Locations.id == locations_id).first()
        if not db_locations:
            return None
        
        update_data = locations_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_locations, field, value)
        
        db.commit()
        db.refresh(db_locations)
        return db_locations
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar ubicación: {e}")
        raise e

def delete_locations(db: Session, locations_id: int):
    """Eliminar una ubicación"""
    try:
        db_locations = db.query(Locations).filter(Locations.id == locations_id).first()
        if not db_locations:
            return False
        
        db.delete(db_locations)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar ubicación: {e}")
        raise e

def get_locations_by_city(db: Session, city: str):
    """Buscar ubicaciones por ciudad"""
    try:
        return db.query(Locations).filter(Locations.city.ilike(f"%{city}%")).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al buscar ubicaciones por ciudad: {e}")
        raise e

def get_locations_by_country(db: Session, country: str):
    """Buscar ubicaciones por país"""
    try:
        return db.query(Locations).filter(Locations.country.ilike(f"%{country}%")).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al buscar ubicaciones por país: {e}")
        raise e
