# Imports de terceros
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_

# Imports del proyecto
from .model_artworks import Artworks
from .schema_artworks import ArtworksCreate, ArtworksUpdate

import logging

logger = logging.getLogger(__name__)

def create_artworks(db: Session, artworks: Artworks):
    """Crear una nueva obra de arte"""
    try:
        db.add(artworks)
        db.commit()
        db.refresh(artworks)
        return artworks
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear artwork: {e}")
        raise e

def get_artworks(db: Session, artworks_id: int):
    """Obtener una obra de arte por ID"""
    try:
        return db.query(Artworks).filter(Artworks.id == artworks_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener artwork: {e}")
        raise e

def get_artworks_by_inventory_code(db: Session, inventory_code: str):
    """Obtener una obra de arte por código de inventario"""
    try:
        return db.query(Artworks).filter(Artworks.inventory_code == inventory_code).first()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener artwork por código: {e}")
        raise e

def get_all_artworks(db: Session, skip: int = 0, limit: int = 100):
    """Obtener todas las obras de arte con paginación"""
    try:
        return db.query(Artworks).order_by(Artworks.id.desc()).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener lista de artworks: {e}")
        raise e

def get_artworks_by_artist(db: Session, artist_id: int, skip: int = 0, limit: int = 100):
    """Obtener obras de arte por artista"""
    try:
        return db.query(Artworks).filter(Artworks.artist_id == artist_id).order_by(Artworks.id.desc()).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener artworks por artista: {e}")
        raise e

def get_available_artworks(db: Session, is_available: bool, skip: int = 0, limit: int = 100):
    """Obtener obras de arte disponibles o no disponibles"""
    try:
        return db.query(Artworks).filter(Artworks.is_available == is_available).order_by(Artworks.id.desc()).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener artworks disponibles: {e}")
        raise e

def update_artworks(db: Session, artworks_id: int, artworks_update: ArtworksUpdate):
    """Actualizar una obra de arte"""
    try:
        db_artworks = db.query(Artworks).filter(Artworks.id == artworks_id).first()
        if not db_artworks:
            return None
        
        update_data = artworks_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_artworks, field, value)
        
        db.commit()
        db.refresh(db_artworks)
        return db_artworks
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar artwork: {e}")
        raise e

def delete_artworks(db: Session, artworks_id: int):
    """Eliminar una obra de arte"""
    try:
        db_artworks = db.query(Artworks).filter(Artworks.id == artworks_id).first()
        if not db_artworks:
            return False
        
        db.delete(db_artworks)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar artwork: {e}")
        raise e

def search_artworks(db: Session, search_term: str, skip: int = 0, limit: int = 100):
    """Buscar obras de arte por título, técnica o materiales"""
    try:
        return db.query(Artworks).filter(
            and_(
                Artworks.title.ilike(f"%{search_term}%") |
                Artworks.technique.ilike(f"%{search_term}%") |
                Artworks.materials.ilike(f"%{search_term}%")
            )
        ).order_by(Artworks.id.desc()).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al buscar artworks: {e}")
        raise e

def mark_artwork_as_sold(db: Session, artworks_id: int):
    """Marcar una obra como vendida"""
    try:
        db_artworks = db.query(Artworks).filter(Artworks.id == artworks_id).first()
        if not db_artworks:
            return None
        
        db_artworks.is_sold = True
        db_artworks.is_available = False
        
        db.commit()
        db.refresh(db_artworks)
        return db_artworks
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al marcar artwork como vendida: {e}")
        raise e
