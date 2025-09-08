# Imports de bibliotecas estándar
from sql_app.Services.app_stock.depositos_tipos.model_depositos_tipos import Depositos_tipos  # Corregida la importación
from typing import List, Optional, Dict, Any
import logging

# Imports de terceros
from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def create_depositos_tipos(db: Session, depositos_tipos: Depositos_tipos) -> Depositos_tipos:
    """
    Crea un nuevo registro de Depositos_tipos en la base de datos usando SQL directo.
    Adaptado para SQL Server usando cláusula OUTPUT para un ID auto incremental.
    """
    try:
        # Preparar los datos para la consulta
        depositos_tipos_data = {}
        
        # Solo incluimos la descripción, el ID será auto incremental
        if hasattr(depositos_tipos, 'descripcion'):
            depositos_tipos_data['descripcion'] = getattr(depositos_tipos, 'descripcion')
        
        # Construir la consulta SQL INSERT con OUTPUT para SQL Server
        query = text("""
            INSERT INTO depositos_tipos (descripcion)
            OUTPUT INSERTED.id, INSERTED.descripcion
            VALUES (:descripcion)
        """)
        
        # Ejecutar la consulta y obtener el registro insertado directamente
        result = db.execute(query, depositos_tipos_data)
        row = result.first()
        db.commit()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El registro no se pudo crear"
            )
        
        # Crear un nuevo objeto Depositos_tipos con los valores devueltos
        new_depositos_tipos = Depositos_tipos()
        new_depositos_tipos.id = row[0]  # El ID generado automáticamente
        new_depositos_tipos.descripcion = row[1]
        
        return new_depositos_tipos
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear Depositos_tipos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el registro: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear Depositos_tipos: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )
def get_depositos_tipos(db: Session, id: int) -> Optional[Depositos_tipos]:
    """
    Obtiene un registro de Depositos_tipos por su clave primaria usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, descripcion FROM depositos_tipos WHERE id = :id"),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depositos_tipos no encontrado.")
        
        # Crear el objeto directamente con los valores
        depositos_tipos = Depositos_tipos()
        depositos_tipos.id = result[0]
        depositos_tipos.descripcion = result[1]
        
        return depositos_tipos
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Depositos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")
def gets_depositos_tipos(db: Session) -> List[Depositos_tipos]:
    """
    Obtiene una lista de todos los registros de Depositos_tipos usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, descripcion FROM depositos_tipos")
        )
        
        depositos_tiposs = []
        for row in result.fetchall():
            depositos_tipos = Depositos_tipos()
            depositos_tipos.id = row[0]
            depositos_tipos.descripcion = row[1]
            depositos_tiposs.append(depositos_tipos)
        
        return depositos_tiposs
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Depositos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")
def delete_depositos_tipos(db: Session, id: int) -> Depositos_tipos:
    """
    Elimina un registro de Depositos_tipos por su clave primaria usando SQL directo.
    """
    try:
        # Obtener y eliminar el registro en una sola operación usando OUTPUT
        result = db.execute(
            text("""
                DELETE FROM depositos_tipos 
                OUTPUT DELETED.id, DELETED.descripcion
                WHERE id = :id
            """),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depositos_tipos no encontrado.")
        
        # Crear el objeto con los datos del registro eliminado
        deleted_depositos_tipos = Depositos_tipos()
        deleted_depositos_tipos.id = result[0]
        deleted_depositos_tipos.descripcion = result[1]
        
        db.commit()
        return deleted_depositos_tipos
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Depositos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")
def update_depositos_tipos(db: Session, id: int, depositos_tipos_data: Dict[str, Any]) -> Depositos_tipos:
    """
    Actualiza un registro de Depositos_tipos por su clave primaria usando SQL directo.
    """
    logger.info(f"Actualizando Depositos_tipos con id = {id}")
    try:
        # Verificar que el registro existe
        result = db.execute(
            text("SELECT COUNT(*) FROM depositos_tipos WHERE id = :id"),
            {"id": id}
        ).scalar()
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depositos_tipos no encontrado.")
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        depositos_tipos_data_copy = depositos_tipos_data.copy()
        if 'id' in depositos_tipos_data_copy:
            del depositos_tipos_data_copy['id']
        
        # Si no hay campos para actualizar, obtener el registro actual
        if not depositos_tipos_data_copy:
            return get_depositos_tipos(db, id)
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in depositos_tipos_data_copy:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa con OUTPUT
        query = text(f"""
            UPDATE depositos_tipos
            SET {set_clause_str}
            OUTPUT INSERTED.id, INSERTED.descripcion
            WHERE id = :id
        """)
        
        # Preparar los parámetros
        params = depositos_tipos_data_copy.copy()
        params['id'] = id
        
        # Ejecutar la consulta
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar el Depositos_tipos.")
        
        # Crear el objeto con los datos actualizados
        updated_depositos_tipos = Depositos_tipos()
        updated_depositos_tipos.id = result[0]
        updated_depositos_tipos.descripcion = result[1]
        
        return updated_depositos_tipos
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Depositos_tipos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")
