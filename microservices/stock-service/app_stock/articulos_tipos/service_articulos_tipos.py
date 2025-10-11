
# Imports de bibliotecas estándar
import logging
from typing import List, Optional, Dict, Any

# Imports de terceros
from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Imports del proyecto
from Services.app_stock.articulos_tipos.model_articulos_tipos import Articulos_tipos

logger = logging.getLogger(__name__)

def create_articulos_tipos(db: Session, articulos_tipos: Articulos_tipos) -> Articulos_tipos:
    """
    Crea un nuevo registro de Articulos_tipos en la base de datos usando SQL directo.
    El ID será generado automáticamente por la base de datos.
    """
    try:
        # Preparar los datos para la consulta
        articulos_tipos_data = {}
        
        if hasattr(articulos_tipos, 'descripcion'):
            articulos_tipos_data['descripcion'] = getattr(articulos_tipos, 'descripcion')
        
        # Construir la consulta SQL INSERT con OUTPUT para SQL Server
        query = text("""
            INSERT INTO articulos_tipos (descripcion)
            OUTPUT INSERTED.id, INSERTED.descripcion
            VALUES (:descripcion)
        """)
        
        # Ejecutar la consulta y obtener el registro insertado directamente
        result = db.execute(query, articulos_tipos_data)
        row = result.first()
        db.commit()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El registro no se pudo crear"
            )
        
        # Crear un nuevo objeto Articulos_tipos con los valores devueltos
        new_articulos_tipos = Articulos_tipos()
        new_articulos_tipos.id = row[0]
        new_articulos_tipos.descripcion = row[1]
        
        return new_articulos_tipos
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear Articulos_tipos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el registro: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear Articulos_tipos: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )

def get_articulos_tipos(db: Session, id: int) -> Optional[Articulos_tipos]:
    """
    Obtiene un registro de Articulos_tipos por su clave primaria usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, descripcion FROM articulos_tipos WHERE id = :id"),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos_tipos no encontrado.")
        
        # Crear el objeto directamente con los valores
        articulos_tipos = Articulos_tipos()
        articulos_tipos.id = result[0]
        articulos_tipos.descripcion = result[1]
        
        return articulos_tipos
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Articulos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")

def gets_articulos_tipos(db: Session) -> List[Articulos_tipos]:
    """
    Obtiene una lista de todos los registros de Articulos_tipos usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, descripcion FROM articulos_tipos")
        )
        
        articulos_tiposs = []
        for row in result.fetchall():
            articulos_tipos = Articulos_tipos()
            articulos_tipos.id = row[0]
            articulos_tipos.descripcion = row[1]
            articulos_tiposs.append(articulos_tipos)
        
        return articulos_tiposs
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Articulos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")

def delete_articulos_tipos(db: Session, id: int) -> Articulos_tipos:
    """
    Elimina un registro de Articulos_tipos por su clave primaria usando SQL directo.
    """
    try:
        # Obtener y eliminar el registro en una sola operación usando OUTPUT
        result = db.execute(
            text("""
                DELETE FROM articulos_tipos 
                OUTPUT DELETED.id, DELETED.descripcion
                WHERE id = :id
            """),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos_tipos no encontrado.")
        
        # Crear el objeto con los datos del registro eliminado
        deleted_articulos_tipos = Articulos_tipos()
        deleted_articulos_tipos.id = result[0]
        deleted_articulos_tipos.descripcion = result[1]
        
        db.commit()
        return deleted_articulos_tipos
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Articulos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")

def update_articulos_tipos(db: Session, id: int, articulos_tipos_data: Dict[str, Any]) -> Articulos_tipos:
    """
    Actualiza un registro de Articulos_tipos por su clave primaria usando SQL directo.
    """
    logger.info(f"Actualizando Articulos_tipos con id = {id}")
    try:
        # Verificar que el registro existe
        result = db.execute(
            text("SELECT COUNT(*) FROM articulos_tipos WHERE id = :id"),
            {"id": id}
        ).scalar()
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos_tipos no encontrado.")
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        articulos_tipos_data_copy = articulos_tipos_data.copy()
        if 'id' in articulos_tipos_data_copy:
            del articulos_tipos_data_copy['id']
        
        # Si no hay campos para actualizar, obtener el registro actual
        if not articulos_tipos_data_copy:
            return get_articulos_tipos(db, id)
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in articulos_tipos_data_copy:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa con OUTPUT
        query = text(f"""
            UPDATE articulos_tipos
            SET {set_clause_str}
            OUTPUT INSERTED.id, INSERTED.descripcion
            WHERE id = :id
        """)
        
        # Preparar los parámetros
        params = articulos_tipos_data_copy.copy()
        params['id'] = id
        
        # Ejecutar la consulta
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar el Articulos_tipos.")
        
        # Crear el objeto con los datos actualizados
        updated_articulos_tipos = Articulos_tipos()
        updated_articulos_tipos.id = result[0]
        updated_articulos_tipos.descripcion = result[1]
        
        return updated_articulos_tipos
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Articulos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")
