from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from sqlalchemy import text
from db.models.familias import Familias
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

def create_familias(db: Session, familias_data: Dict[str, Any]) -> Familias:
    """
    Crea un nuevo registro de Familias en la base de datos usando SQL directo.
    """
    try:
        # Construir la consulta SQL INSERT
        query = text("""
            INSERT INTO familias (tetwe, asd)
            VALUES (:tetwe, :asd)
            RETURNING *
        """)
        
        # Ejecutar la consulta
        result = db.execute(query, familias_data)
        db.commit()
        
        # Convertir el resultado a diccionario
        record_dict = dict(result.fetchone())
        
        # Crear y devolver una instancia del modelo
        return Familias(**record_dict)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Familias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear el registro: {str(e)}")

def get_familias(db: Session, tetwe: int) -> Optional[Familias]:
    """
    Obtiene un registro de Familias por su clave primaria usando SQL directo.
    """
    try:
        query = text("""
            SELECT * FROM familias
            WHERE tetwe = :tetwe
        """)
        
        result = db.execute(query, {tetwe: tetwe})
        record = result.fetchone()
        
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Familias no encontrado.")
        
        # Convertir el resultado a diccionario y crear una instancia del modelo
        record_dict = dict(record)
        return Familias(**record_dict)
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Familias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")

def gets_familias(db: Session) -> List[Familias]:
    """
    Obtiene una lista de todos los registros de Familias usando SQL directo.
    """
    try:
        query = text("""
            SELECT * FROM familias
        """)
        
        result = db.execute(query)
        records = []
        
        for row in result:
            record_dict = dict(row)
            records.append(Familias(**record_dict))
        
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Familias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")

def delete_familias(db: Session, tetwe: int) -> Dict[str, Any]:
    """
    Elimina un registro de Familias por su clave primaria usando SQL directo.
    """
    try:
        # Primero obtenemos el registro para verificar que existe
        get_query = text("""
            SELECT * FROM familias
            WHERE tetwe = :tetwe
        """)
        
        result = db.execute(get_query, {tetwe: tetwe})
        record = result.fetchone()
        
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Familias no encontrado.")
        
        # Si existe, procedemos a eliminarlo
        delete_query = text("""
            DELETE FROM familias
            WHERE tetwe = :tetwe
            RETURNING *
        """)
        
        result = db.execute(delete_query, {tetwe: tetwe})
        deleted_record = dict(result.fetchone())
        db.commit()
        
        return deleted_record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Familias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")

def update_familias(db: Session, tetwe: int, familias_data: Dict[str, Any]) -> Familias:
    """
    Actualiza un registro de Familias por su clave primaria usando SQL directo.
    """
    logger.info(f"Actualizando Familias con tetwe = {tetwe}")
    try:
        # Primero verificamos que el registro existe
        check_query = text("""
            SELECT * FROM familias
            WHERE tetwe = :tetwe
        """)
        
        result = db.execute(check_query, {tetwe: tetwe})
        if not result.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Familias no encontrado.")
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        familias_data_copy = familias_data.copy()
        if 'tetwe' in familias_data_copy:
            del familias_data_copy['tetwe']
        
        # Si no hay campos para actualizar, retornar el registro como está
        if not familias_data_copy:
            get_query = text("""
                SELECT * FROM familias
                WHERE tetwe = :tetwe
            """)
            result = db.execute(get_query, {tetwe: tetwe})
            record_dict = dict(result.fetchone())
            return Familias(**record_dict)
        
        # Construir la consulta de actualización dinámica
        set_clauses = ", ".join([f"{field} = :{field}" for field in familias_data_copy.keys()])
        update_query = text(f"""
            UPDATE familias
            SET {set_clauses}
            WHERE tetwe = :tetwe
            RETURNING *
        """)
        
        # Agregar la clave primaria al diccionario de parámetros
        params = familias_data_copy.copy()
        params['tetwe'] = tetwe
        
        # Ejecutar la actualización
        result = db.execute(update_query, params)
        updated_record = result.fetchone()
        db.commit()
        
        return Familias(**dict(updated_record))
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Familias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")

