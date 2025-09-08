
# Imports de bibliotecas estándar
import logging
from typing import List, Optional, Dict, Any

# Imports de terceros
from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Imports del proyecto
from sql_app.Services.app_stock.articulos_series.model_articulos_series import Articulos_series

logger = logging.getLogger(__name__)

def create_articulos_series(db: Session, articulos_series: Articulos_series) -> Articulos_series:
    """
    Crea un nuevo registro de Articulos_series en la base de datos usando SQL directo.
    Adaptado para SQL Server usando cláusula OUTPUT e ID autoincremental.
    """
    try:
        # Preparar los datos para la consulta
        articulos_series_data = {}
        
        # Solo incluimos el campo serie, permitiendo que el ID sea autogenerado
        if hasattr(articulos_series, 'serie'):
            articulos_series_data['serie'] = getattr(articulos_series, 'serie')
        
        # Construir la consulta SQL INSERT con OUTPUT para SQL Server, sin incluir el campo ID
        query = text("""
            INSERT INTO articulos_series (serie)
            OUTPUT INSERTED.id, INSERTED.serie
            VALUES (:serie)
        """)
        
        # Ejecutar la consulta y obtener el registro insertado directamente
        result = db.execute(query, articulos_series_data)
        row = result.first()
        db.commit()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El registro no se pudo crear"
            )
        
        # Crear un nuevo objeto Articulos_series con los valores devueltos
        new_articulos_series = Articulos_series()
        new_articulos_series.id = row[0]
        new_articulos_series.serie = row[1]
        
        return new_articulos_series
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear Articulos_series: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el registro: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear Articulos_series: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )

def get_articulos_series(db: Session, id: int) -> Optional[Articulos_series]:
    """
    Obtiene un registro de Articulos_series por su clave primaria usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, serie FROM articulos_series WHERE id = :id"),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos_series no encontrado.")
        
        # Crear el objeto directamente con los valores
        articulos_series = Articulos_series()
        articulos_series.id = result[0]
        articulos_series.serie = result[1]
        
        return articulos_series
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Articulos_series: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")

def gets_articulos_series(db: Session) -> List[Articulos_series]:
    """
    Obtiene una lista de todos los registros de Articulos_series usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, serie FROM articulos_series")
        )
        
        articulos_seriess = []
        for row in result.fetchall():
            articulos_series = Articulos_series()
            articulos_series.id = row[0]
            articulos_series.serie = row[1]
            articulos_seriess.append(articulos_series)
        
        return articulos_seriess
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Articulos_series: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")

def delete_articulos_series(db: Session, id: int) -> Articulos_series:
    """
    Elimina un registro de Articulos_series por su clave primaria usando SQL directo.
    """
    try:
        # Obtener y eliminar el registro en una sola operación usando OUTPUT
        result = db.execute(
            text("""
                DELETE FROM articulos_series 
                OUTPUT DELETED.id, DELETED.serie
                WHERE id = :id
            """),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos_series no encontrado.")
        
        # Crear el objeto con los datos del registro eliminado
        deleted_articulos_series = Articulos_series()
        deleted_articulos_series.id = result[0]
        deleted_articulos_series.serie = result[1]
        
        db.commit()
        return deleted_articulos_series
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Articulos_series: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")

def update_articulos_series(db: Session, id: int, articulos_series_data: Dict[str, Any]) -> Articulos_series:
    """
    Actualiza un registro de Articulos_series por su clave primaria usando SQL directo.
    """
    logger.info(f"Actualizando Articulos_series con id = {id}")
    try:
        # Verificar que el registro existe
        result = db.execute(
            text("SELECT COUNT(*) FROM articulos_series WHERE id = :id"),
            {"id": id}
        ).scalar()
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos_series no encontrado.")
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        articulos_series_data_copy = articulos_series_data.copy()
        if 'id' in articulos_series_data_copy:
            del articulos_series_data_copy['id']
        
        # Si no hay campos para actualizar, obtener el registro actual
        if not articulos_series_data_copy:
            return get_articulos_series(db, id)
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in articulos_series_data_copy:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa con OUTPUT
        query = text(f"""
            UPDATE articulos_series
            SET {set_clause_str}
            OUTPUT INSERTED.id, INSERTED.serie
            WHERE id = :id
        """)
        
        # Preparar los parámetros
        params = articulos_series_data_copy.copy()
        params['id'] = id
        
        # Ejecutar la consulta
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar el Articulos_series.")
        
        # Crear el objeto con los datos actualizados
        updated_articulos_series = Articulos_series()
        updated_articulos_series.id = result[0]
        updated_articulos_series.serie = result[1]
        
        return updated_articulos_series
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Articulos_series: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")
