from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from sqlalchemy import text
from .model_ot import Ot  # Corregida la importación
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

def create_ot(db: Session, ot: Ot) -> Ot:
    """
    Crea un nuevo registro de Ot en la base de datos usando SQL directo.
    Adaptado para SQL Server usando cláusula OUTPUT.
    """
    try:
        # Preparar los datos para la consulta
        ot_data = {}
        
        for field in ['id', 'id_trabajo', 'area', 'personal', 'tiempo_estimado']:
            if hasattr(ot, field):
                ot_data[field] = getattr(ot, field)
        
        # Construir la consulta SQL INSERT con OUTPUT para SQL Server
        query = text("""
            INSERT INTO ot (id, id_trabajo, area, personal, tiempo_estimado)
            OUTPUT INSERTED.id, INSERTED.id_trabajo, INSERTED.area, INSERTED.personal, INSERTED.tiempo_estimado
            VALUES (:id, :id_trabajo, :area, :personal, :tiempo_estimado)
        """)
        
        # Ejecutar la consulta y obtener el registro insertado directamente
        result = db.execute(query, ot_data)
        row = result.first()
        db.commit()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El registro no se pudo crear"
            )
        
        # Crear un nuevo objeto Ot con los valores devueltos
        new_ot = Ot()
        new_ot.id = row[0]
        new_ot.id_trabajo = row[1]
        new_ot.area = row[2]
        new_ot.personal = row[3]
        new_ot.tiempo_estimado = row[4]
        
        return new_ot
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear Ot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el registro: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear Ot: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )
def get_ot(db: Session, id: int) -> Optional[Ot]:
    """
    Obtiene un registro de Ot por su clave primaria usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, id_trabajo, area, personal, tiempo_estimado FROM ot WHERE id = :id"),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ot no encontrado.")
        
        # Crear el objeto directamente con los valores
        ot = Ot()
        ot.id = result[0]
        ot.id_trabajo = result[1]
        ot.area = result[2]
        ot.personal = result[3]
        ot.tiempo_estimado = result[4]
        
        return ot
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Ot: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")
def gets_ot(db: Session) -> List[Ot]:
    """
    Obtiene una lista de todos los registros de Ot usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, id_trabajo, area, personal, tiempo_estimado FROM ot")
        )
        
        ots = []
        for row in result.fetchall():
            ot = Ot()
            ot.id = row[0]
            ot.id_trabajo = row[1]
            ot.area = row[2]
            ot.personal = row[3]
            ot.tiempo_estimado = row[4]
            ots.append(ot)
        
        return ots
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Ot: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")
def delete_ot(db: Session, id: int) -> Ot:
    """
    Elimina un registro de Ot por su clave primaria usando SQL directo.
    """
    try:
        # Obtener y eliminar el registro en una sola operación usando OUTPUT
        result = db.execute(
            text("""
                DELETE FROM ot 
                OUTPUT DELETED.id, DELETED.id_trabajo, DELETED.area, DELETED.personal, DELETED.tiempo_estimado
                WHERE id = :id
            """),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ot no encontrado.")
        
        # Crear el objeto con los datos del registro eliminado
        deleted_ot = Ot()
        deleted_ot.id = result[0]
        deleted_ot.id_trabajo = result[1]
        deleted_ot.area = result[2]
        deleted_ot.personal = result[3]
        deleted_ot.tiempo_estimado = result[4]
        
        db.commit()
        return deleted_ot
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Ot: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")
def update_ot(db: Session, id: int, ot_data: Dict[str, Any]) -> Ot:
    """
    Actualiza un registro de Ot por su clave primaria usando SQL directo.
    """
    logger.info(f"Actualizando Ot con id = {id}")
    try:
        # Verificar que el registro existe
        result = db.execute(
            text("SELECT COUNT(*) FROM ot WHERE id = :id"),
            {"id": id}
        ).scalar()
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ot no encontrado.")
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        ot_data_copy = ot_data.copy()
        if 'id' in ot_data_copy:
            del ot_data_copy['id']
        
        # Si no hay campos para actualizar, obtener el registro actual
        if not ot_data_copy:
            return get_ot(db, id)
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in ot_data_copy:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa con OUTPUT
        query = text(f"""
            UPDATE ot
            SET {set_clause_str}
            OUTPUT INSERTED.id, INSERTED.id_trabajo, INSERTED.area, INSERTED.personal, INSERTED.tiempo_estimado
            WHERE id = :id
        """)
        
        # Preparar los parámetros
        params = ot_data_copy.copy()
        params['id'] = id
        
        # Ejecutar la consulta
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar el Ot.")
        
        # Crear el objeto con los datos actualizados
        updated_ot = Ot()
        updated_ot.id = result[0]
        updated_ot.id_trabajo = result[1]
        updated_ot.area = result[2]
        updated_ot.personal = result[3]
        updated_ot.tiempo_estimado = result[4]
        
        return updated_ot
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Ot: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")
