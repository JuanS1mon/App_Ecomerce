from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from sqlalchemy import text
from .model_facu import Facu
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)
def create_facu(db: Session, facu: Facu) -> Facu:
    try:
        # Convertir el objeto Facu a un diccionario para la consulta SQL
        facu_data = {
            "id": facu.id,
            "asd": facu.asd
        }
        query = text("""
            INSERT INTO facu (id, asd)
            VALUES (:id, :asd)
            RETURNING *
        """)
        
        result = db.execute(query, facu_data)
        db.commit()
        
        record_dict = dict(result.fetchone())
        return Facu(**record_dict)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Facu: {e}")
        raise HTTPException(...)

def get_facu(db: Session, id: int) -> Optional[Facu]:
    """
    Obtiene un registro de Facu por su clave primaria usando SQL directo.
    """
    try:
        query = text("""
            SELECT * FROM facu
            WHERE id = :id
        """)
        
        result = db.execute(query, {id: id})
        record = result.fetchone()
        
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facu no encontrado.")
        
        # Convertir el resultado a diccionario y crear una instancia del modelo
        record_dict = dict(record)
        return Facu(**record_dict)
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Facu: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")

def gets_facu(db: Session) -> List[Facu]:
    """
    Obtiene una lista de todos los registros de Facu usando SQL directo.
    """
    try:
        query = text("""
            SELECT * FROM facu
        """)
        
        result = db.execute(query)
        records = []
        
        for row in result:
            record_dict = dict(row)
            records.append(Facu(**record_dict))
        
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Facu: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")

def delete_facu(db: Session, id: int) -> Dict[str, Any]:
    """
    Elimina un registro de Facu por su clave primaria usando SQL directo.
    """
    try:
        # Primero obtenemos el registro para verificar que existe
        get_query = text("""
            SELECT * FROM facu
            WHERE id = :id
        """)
        
        result = db.execute(get_query, {id: id})
        record = result.fetchone()
        
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facu no encontrado.")
        
        # Si existe, procedemos a eliminarlo
        delete_query = text("""
            DELETE FROM facu
            WHERE id = :id
            RETURNING *
        """)
        
        result = db.execute(delete_query, {id: id})
        deleted_record = dict(result.fetchone())
        db.commit()
        
        return deleted_record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Facu: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")

def update_facu(db: Session, id: int, facu_data: Dict[str, Any]) -> Facu:
    """
    Actualiza un registro de Facu por su clave primaria usando SQL directo.
    """
    logger.info(f"Actualizando Facu con id = {id}")
    try:
        # Primero verificamos que el registro existe
        check_query = text("""
            SELECT * FROM facu
            WHERE id = :id
        """)
        
        result = db.execute(check_query, {id: id})
        if not result.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facu no encontrado.")
        
        # Eliminar la clave primaria del diccionario de datos si est� presente
        facu_data_copy = facu_data.copy()
        if 'id' in facu_data_copy:
            del facu_data_copy['id']
        
        # Si no hay campos para actualizar, retornar el registro como est�
        if not facu_data_copy:
            get_query = text("""
                SELECT * FROM facu
                WHERE id = :id
            """)
            result = db.execute(get_query, {id: id})
            record_dict = dict(result.fetchone())
            return Facu(**record_dict)
        
        # Construir la consulta de actualizaci�n din�mica
        set_clauses = ", ".join([f"{field} = :{field}" for field in facu_data_copy.keys()])
        update_query = text(f"""
            UPDATE facu
            SET {set_clauses}
            WHERE id = :id
            RETURNING *
        """)
        
        # Agregar la clave primaria al diccionario de par�metros
        params = facu_data_copy.copy()
        params['id'] = id
        
        # Ejecutar la actualizaci�n
        result = db.execute(update_query, params)
        updated_record = result.fetchone()
        db.commit()
        
        return Facu(**dict(updated_record))
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Facu: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")

