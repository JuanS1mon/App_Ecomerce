# Imports de terceros
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Imports del proyecto
from .model_documents import Documents
from .schema_documents import DocumentsCreate, DocumentsUpdate

import logging

logger = logging.getLogger(__name__)

def create_documents(db: Session, documents: Documents):
    """Crear un nuevo documento"""
    try:
        db.add(documents)
        db.commit()
        db.refresh(documents)
        return documents
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear documento: {e}")
        raise e

def get_documents(db: Session, documents_id: int):
    """Obtener un documento por ID"""
    try:
        return db.query(Documents).filter(Documents.id == documents_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener documento: {e}")
        raise e

def get_all_documents(db: Session, skip: int = 0, limit: int = 100):
    """Obtener todos los documentos con paginación"""
    try:
        return db.query(Documents).order_by(Documents.id.desc()).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener lista de documentos: {e}")
        raise e

def get_documents_by_artwork(db: Session, artwork_id: int):
    """Obtener documentos por obra de arte"""
    try:
        return db.query(Documents).filter(Documents.artwork_id == artwork_id).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener documentos por obra: {e}")
        raise e

def get_documents_by_type(db: Session, doc_type: str):
    """Obtener documentos por tipo"""
    try:
        return db.query(Documents).filter(Documents.doc_type.ilike(f"%{doc_type}%")).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener documentos por tipo: {e}")
        raise e

def update_documents(db: Session, documents_id: int, documents_update: DocumentsUpdate):
    """Actualizar un documento"""
    try:
        db_documents = db.query(Documents).filter(Documents.id == documents_id).first()
        if not db_documents:
            return None
        
        update_data = documents_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_documents, field, value)
        
        db.commit()
        db.refresh(db_documents)
        return db_documents
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar documento: {e}")
        raise e

def delete_documents(db: Session, documents_id: int):
    """Eliminar un documento"""
    try:
        db_documents = db.query(Documents).filter(Documents.id == documents_id).first()
        if not db_documents:
            return False
        
        db.delete(db_documents)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar documento: {e}")
        raise e

def search_documents_by_url(db: Session, url_fragment: str):
    """Buscar documentos por fragmento de URL"""
    try:
        return db.query(Documents).filter(Documents.url.ilike(f"%{url_fragment}%")).all()
    except SQLAlchemyError as e:
        logger.error(f"Error al buscar documentos por URL: {e}")
        raise e

def get_document_types_summary(db: Session):
    """Obtener resumen de tipos de documentos"""
    try:
        # Obtener todos los tipos únicos y contarlos
        from sqlalchemy import func
        result = db.query(
            Documents.doc_type,
            func.count(Documents.id).label('count')
        ).group_by(Documents.doc_type).all()
        
        return [{"doc_type": row.doc_type, "count": row.count} for row in result]
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener resumen de tipos de documentos: {e}")
        raise e
