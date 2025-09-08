# Imports de terceros
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Imports del proyecto
from .model_artwork_states import ArtworkStates
from .schema_artwork_states import ArtworkStatesCreate, ArtworkStatesUpdate

import logging

logger = logging.getLogger(__name__)

def create_artwork_states(db: Session, artwork_states: ArtworkStates):
    """Crear un nuevo estado de obra"""
    try:
        db.add(artwork_states)
        db.commit()
        db.refresh(artwork_states)
        return artwork_states
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear estado de obra: {e}")
        raise e

def get_artwork_states(db: Session, state_id: int):
    """Obtener un estado de obra por ID"""
    try:
        return db.query(ArtworkStates).filter(ArtworkStates.id == state_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener estado de obra: {e}")
        raise e

def get_all_artwork_states(db: Session, skip: int = 0, limit: int = 100):
    """Obtener todos los estados de obra con paginación"""
    try:
        return db.query(ArtworkStates).order_by(ArtworkStates.id.desc()).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener lista de estados de obra: {e}")
        raise e

def update_artwork_states(db: Session, state_id: int, state_update: ArtworkStatesUpdate):
    """Actualizar un estado de obra"""
    try:
        db_state = db.query(ArtworkStates).filter(ArtworkStates.id == state_id).first()
        if not db_state:
            return None
        
        update_data = state_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_state, field, value)
        
        db.commit()
        db.refresh(db_state)
        return db_state
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar estado de obra: {e}")
        raise e

def delete_artwork_states(db: Session, state_id: int):
    """Eliminar un estado de obra"""
    try:
        db_state = db.query(ArtworkStates).filter(ArtworkStates.id == state_id).first()
        if not db_state:
            return False
        
        db.delete(db_state)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar estado de obra: {e}")
        raise e
