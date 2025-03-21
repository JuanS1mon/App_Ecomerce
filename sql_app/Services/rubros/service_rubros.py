from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from sqlalchemy import text
from db.models.rubros import Rubros
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

def create_rubros(db: Session, rubros_data: Dict[str, Any]) -> Rubros:
    """
    Crea un nuevo registro de Rubros en la base de datos usando SQL directo.
    """
    try:
        # Construir la consulta SQL INSERT
        query = text("""
            INSERT INTO rubros (codigo, test1, test2, test3)
            VALUES (:codigo, :test1, :test2, :test3)
            RETURNING *
        """)
        
        # Ejecutar la consulta
        result = db.execute(query, rubros_data)
        db.commit()
        
        # Convertir el resultado a diccionario
        record_dict = dict(result.fetchone())
        
        # Crear y devolver una instancia del modelo
        return Rubros(**record_dict)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear Rubros: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear el registro: {str(e)}")

def get_rubros(db: Session, codigo: int) -> Optional[Rubros]:
    """
    Obtiene un registro de Rubros por su clave primaria usando SQL directo.
    """
    try:
        query = text("""
            SELECT * FROM rubros
            WHERE codigo = :codigo
        """)
        
        result = db.execute(query, {codigo: codigo})
        record = result.fetchone()
        
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubros no encontrado.")
        
        # Convertir el resultado a diccionario y crear una instancia del modelo
        record_dict = dict(record)
        return Rubros(**record_dict)
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Rubros: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")

def gets_rubros(db: Session) -> List[Rubros]:
    """
    Obtiene una lista de todos los registros de Rubros usando SQL directo.
    """
    try:
        query = text("""
            SELECT * FROM rubros
        """)
        
        result = db.execute(query)
        records = []
        
        for row in result:
            record_dict = dict(row)
            records.append(Rubros(**record_dict))
        
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Rubros: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")

def delete_rubros(db: Session, codigo: int) -> Dict[str, Any]:
    """
    Elimina un registro de Rubros por su clave primaria usando SQL directo.
    """
    try:
        # Primero obtenemos el registro para verificar que existe
        get_query = text("""
            SELECT * FROM rubros
            WHERE codigo = :codigo
        """)
        
        result = db.execute(get_query, {codigo: codigo})
        record = result.fetchone()
        
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubros no encontrado.")
        
        # Si existe, procedemos a eliminarlo
        delete_query = text("""
            DELETE FROM rubros
            WHERE codigo = :codigo
            RETURNING *
        """)
        
        result = db.execute(delete_query, {codigo: codigo})
        deleted_record = dict(result.fetchone())
        db.commit()
        
        return deleted_record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Rubros: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")

def update_rubros(db: Session, codigo: int, rubros_data: Dict[str, Any]) -> Rubros:
    """
    Actualiza un registro de Rubros por su clave primaria usando SQL directo.
    """
    logger.info(f"Actualizando Rubros con codigo = {codigo}")
    try:
        # Primero verificamos que el registro existe
        check_query = text("""
            SELECT * FROM rubros
            WHERE codigo = :codigo
        """)
        
        result = db.execute(check_query, {codigo: codigo})
        if not result.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubros no encontrado.")
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        rubros_data_copy = rubros_data.copy()
        if 'codigo' in rubros_data_copy:
            del rubros_data_copy['codigo']
        
        # Si no hay campos para actualizar, retornar el registro como está
        if not rubros_data_copy:
            get_query = text("""
                SELECT * FROM rubros
                WHERE codigo = :codigo
            """)
            result = db.execute(get_query, {codigo: codigo})
            record_dict = dict(result.fetchone())
            return Rubros(**record_dict)
        
        # Construir la consulta de actualización dinámica
        set_clauses = ", ".join([f"{field} = :{field}" for field in rubros_data_copy.keys()])
        update_query = text(f"""
            UPDATE rubros
            SET {set_clauses}
            WHERE codigo = :codigo
            RETURNING *
        """)
        
        # Agregar la clave primaria al diccionario de parámetros
        params = rubros_data_copy.copy()
        params['codigo'] = codigo
        
        # Ejecutar la actualización
        result = db.execute(update_query, params)
        updated_record = result.fetchone()
        db.commit()
        
        return Rubros(**dict(updated_record))
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Rubros: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")

