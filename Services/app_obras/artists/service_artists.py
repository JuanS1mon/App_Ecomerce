# Imports de terceros
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Imports del proyecto
from .model_artists import Artists
from .schema_artists import ArtistsCreate, ArtistsUpdate

import logging

logger = logging.getLogger(__name__)

def create_artists(db: Session, artists: Artists):
    """Crear un nuevo artista"""
    try:
        db.add(artists)
        db.commit()
        db.refresh(artists)
        return artists
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear artista: {e}")
        raise e

def get_artists(db: Session, artists_id: int):
    """Obtener un artista por ID"""
    try:
        return db.query(Artists).filter(Artists.id == artists_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener artista: {e}")
        raise e

def get_all_artists(db: Session, skip: int = 0, limit: int = 100):
    """Obtener todos los artistas con paginación"""
    try:
        return db.query(Artists).order_by(Artists.id.desc()).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener lista de artistas: {e}")
        raise e

def update_artists(db: Session, artists_id: int, artists_update: ArtistsUpdate):
    """Actualizar un artista"""
    try:
        db_artists = db.query(Artists).filter(Artists.id == artists_id).first()
        if not db_artists:
            return None
        
        update_data = artists_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_artists, field, value)
        
        db.commit()
        db.refresh(db_artists)
        return db_artists
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar artista: {e}")
        raise e

def delete_artists(db: Session, artists_id: int):
    """Eliminar un artista"""
    try:
        db_artists = db.query(Artists).filter(Artists.id == artists_id).first()
        if not db_artists:
            return False
        
        db.delete(db_artists)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar artista: {e}")
        raise e

def get_artists_by_name(db: Session, name: str):
    """Buscar artistas por nombre"""
    try:
        return db.query(Artists).filter(Artists.full_name.ilike(f"%{name}%")).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al buscar artistas por nombre: {e}")
        raise e
