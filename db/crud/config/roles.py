# Imports de bibliotecas estándar
import logging

# Imports de terceros
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Configura el logger
logger = logging.getLogger(__name__)

def create_role(db: Session, nombre: str, descripcion: str = None):
    """Crea un nuevo rol"""
    try:
        result = db.execute(
            text("""
                INSERT INTO roles (nombre, descripcion)
                OUTPUT INSERTED.id, INSERTED.nombre, INSERTED.descripcion
                VALUES (:nombre, :descripcion)
            """),
            {"nombre": nombre, "descripcion": descripcion}
        )
        
        row = result.first()
        db.commit()
        
        if row:
            return {"id": row[0], "nombre": row[1], "descripcion": row[2]}
        return None
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear rol: {str(e)}")
        raise HTTPException(status_code=400, detail=f"No se pudo crear el rol: {str(e)}")

def get_role_by_name(db: Session, nombre: str):
    """Obtiene un rol por su nombre"""
    try:
        result = db.execute(
            text("SELECT id, nombre, descripcion FROM roles WHERE nombre = :nombre"),
            {"nombre": nombre}
        ).first()
        
        if not result:
            return None
        
        return {"id": result[0], "nombre": result[1], "descripcion": result[2]}
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener rol: {str(e)}")
        return None

def get_all_roles(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene todos los roles"""
    try:
        result = db.execute(
            text("SELECT id, nombre, descripcion FROM roles ORDER BY nombre OFFSET :skip ROWS FETCH NEXT :limit ROWS ONLY"),
            {"skip": skip, "limit": limit}
        )
        
        roles = result.fetchall()
        return [{"id": role[0], "nombre": role[1], "descripcion": role[2]} for role in roles]
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener roles: {str(e)}")
        return []

def delete_role(db: Session, role_id: int):
    """Elimina un rol"""
    try:
        # Primero eliminar todas las relaciones con usuarios
        db.execute(
            text("DELETE FROM usuario_roles WHERE role_id = :role_id"),
            {"role_id": role_id}
        )
        
        # Luego eliminar el rol
        result = db.execute(
            text("DELETE FROM roles WHERE id = :role_id"),
            {"role_id": role_id}
        )
        
        deleted = result.rowcount > 0
        db.commit()
        return deleted
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar rol: {str(e)}")
        raise HTTPException(status_code=400, detail=f"No se pudo eliminar el rol: {str(e)}")