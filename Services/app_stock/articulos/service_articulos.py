from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from sqlalchemy import text
from .model_articulos import Articulos  # Corregida la importación
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

def create_articulos(db: Session, articulos: Articulos) -> Articulos:
    """
    Crea un nuevo registro de Articulos en la base de datos usando SQL directo.
    Adaptado para SQL Server usando cláusula OUTPUT.
    """
    try:
        # Preparar los datos para la consulta
        articulos_data = {}
        
        for field in ['id', 'codigo', 'descripcion', 'preciocosto', 'modelo', 'marca', 'id_tipo']:
            if hasattr(articulos, field):
                articulos_data[field] = getattr(articulos, field)
        
        # Construir la consulta SQL INSERT con OUTPUT para SQL Server
        query = text("""
            INSERT INTO articulos (id, codigo, descripcion, preciocosto, modelo, marca, id_tipo)
            OUTPUT INSERTED.id, INSERTED.codigo, INSERTED.descripcion, INSERTED.preciocosto, INSERTED.modelo, INSERTED.marca, INSERTED.id_tipo
            VALUES (:id, :codigo, :descripcion, :preciocosto, :modelo, :marca, :id_tipo)
        """)
        
        # Ejecutar la consulta y obtener el registro insertado directamente
        result = db.execute(query, articulos_data)
        row = result.first()
        db.commit()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El registro no se pudo crear"
            )
        
        # Crear un nuevo objeto Articulos con los valores devueltos
        new_articulos = Articulos()
        new_articulos.id = row[0]
        new_articulos.codigo = row[1]
        new_articulos.descripcion = row[2]
        new_articulos.preciocosto = row[3]
        new_articulos.modelo = row[4]
        new_articulos.marca = row[5]
        new_articulos.id_tipo = row[6]
        
        return new_articulos
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear Articulos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el registro: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear Articulos: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )
def get_articulos(db: Session, id: int) -> Optional[Articulos]:
    """
    Obtiene un registro de Articulos por su clave primaria usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, codigo, descripcion, preciocosto, modelo, marca, id_tipo FROM articulos WHERE id = :id"),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos no encontrado.")
        
        # Crear el objeto directamente con los valores
        articulos = Articulos()
        articulos.id = result[0]
        articulos.codigo = result[1]
        articulos.descripcion = result[2]
        articulos.preciocosto = result[3]
        articulos.modelo = result[4]
        articulos.marca = result[5]
        articulos.id_tipo = result[6]
        
        return articulos
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")
def gets_articulos(db: Session) -> List[Articulos]:
    """
    Obtiene una lista de todos los registros de Articulos usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, codigo, descripcion, preciocosto, modelo, marca, id_tipo FROM articulos")
        )
        
        articuloss = []
        for row in result.fetchall():
            articulos = Articulos()
            articulos.id = row[0]
            articulos.codigo = row[1]
            articulos.descripcion = row[2]
            articulos.preciocosto = row[3]
            articulos.modelo = row[4]
            articulos.marca = row[5]
            articulos.id_tipo = row[6]
            articuloss.append(articulos)
        
        return articuloss
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")
def delete_articulos(db: Session, id: int) -> Articulos:
    """
    Elimina un registro de Articulos por su clave primaria usando SQL directo.
    """
    try:
        # Obtener y eliminar el registro en una sola operación usando OUTPUT
        result = db.execute(
            text("""
                DELETE FROM articulos 
                OUTPUT DELETED.id, DELETED.codigo, DELETED.descripcion, DELETED.preciocosto, DELETED.modelo, DELETED.marca, DELETED.id_tipo
                WHERE id = :id
            """),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos no encontrado.")
        
        # Crear el objeto con los datos del registro eliminado
        deleted_articulos = Articulos()
        deleted_articulos.id = result[0]
        deleted_articulos.codigo = result[1]
        deleted_articulos.descripcion = result[2]
        deleted_articulos.preciocosto = result[3]
        deleted_articulos.modelo = result[4]
        deleted_articulos.marca = result[5]
        deleted_articulos.id_tipo = result[6]
        
        db.commit()
        return deleted_articulos
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")
def update_articulos(db: Session, id: int, articulos_data: Dict[str, Any]) -> Articulos:
    """
    Actualiza un registro de Articulos por su clave primaria usando SQL directo.
    """
    logger.info(f"Actualizando Articulos con id = {id}")
    try:
        # Verificar que el registro existe
        result = db.execute(
            text("SELECT COUNT(*) FROM articulos WHERE id = :id"),
            {"id": id}
        ).scalar()
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articulos no encontrado.")
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        articulos_data_copy = articulos_data.copy()
        if 'id' in articulos_data_copy:
            del articulos_data_copy['id']
        
        # Si no hay campos para actualizar, obtener el registro actual
        if not articulos_data_copy:
            return get_articulos(db, id)
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in articulos_data_copy:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa con OUTPUT
        query = text(f"""
            UPDATE articulos
            SET {set_clause_str}
            OUTPUT INSERTED.id, INSERTED.codigo, INSERTED.descripcion, INSERTED.preciocosto, INSERTED.modelo, INSERTED.marca, INSERTED.id_tipo
            WHERE id = :id
        """)
        
        # Preparar los parámetros
        params = articulos_data_copy.copy()
        params['id'] = id
        
        # Ejecutar la consulta
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar el Articulos.")
        
        # Crear el objeto con los datos actualizados
        updated_articulos = Articulos()
        updated_articulos.id = result[0]
        updated_articulos.codigo = result[1]
        updated_articulos.descripcion = result[2]
        updated_articulos.preciocosto = result[3]
        updated_articulos.modelo = result[4]
        updated_articulos.marca = result[5]
        updated_articulos.id_tipo = result[6]
        
        return updated_articulos
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Articulos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")
