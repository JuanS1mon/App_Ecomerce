# Imports de bibliotecas estándar
from Services.app_stock.depositos.model_depositos import Depositos  # Corregida la importación
from typing import List, Optional, Dict, Any
import logging

# Imports de terceros
from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def create_depositos(db: Session, depositos: Depositos) -> Depositos:
    """
    Crea un nuevo registro de Depositos en la base de datos usando SQL directo.
    Adaptado para SQL Server usando cláusula OUTPUT para un ID auto incremental.
    """
    try:
        # Preparar los datos para la consulta
        depositos_data = {}
        
        # Excluimos el ID ya que es auto incremental
        for field in ['descripcion', 'codigo', 'observacion']:
            if hasattr(depositos, field):
                depositos_data[field] = getattr(depositos, field)
        
        # Construir la consulta SQL INSERT con OUTPUT para SQL Server
        # Sin incluir el ID en los valores
        query = text("""
            INSERT INTO depositos (descripcion, codigo, observacion)
            OUTPUT INSERTED.id, INSERTED.descripcion, INSERTED.codigo, INSERTED.observacion
            VALUES (:descripcion, :codigo, :observacion)
        """)
        
        # Ejecutar la consulta y obtener el registro insertado directamente
        result = db.execute(query, depositos_data)
        row = result.first()
        db.commit()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El registro no se pudo crear"
            )
        
        # Crear un nuevo objeto Depositos con los valores devueltos
        new_depositos = Depositos()
        new_depositos.id = row[0]  # El ID generado automáticamente
        new_depositos.descripcion = row[1]
        new_depositos.codigo = row[2]
        new_depositos.observacion = row[3]
        
        return new_depositos
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear Depositos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el registro: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear Depositos: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )
def get_depositos(db: Session, id: int) -> Optional[Depositos]:
    """
    Obtiene un registro de Depositos por su clave primaria usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, descripcion, codigo, observacion FROM depositos WHERE id = :id"),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depositos no encontrado.")
        
        # Crear el objeto directamente con los valores
        depositos = Depositos()
        depositos.id = result[0]
        depositos.descripcion = result[1]
        depositos.codigo = result[2]
        depositos.observacion = result[3]
        
        return depositos
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Depositos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")
def gets_depositos(db: Session) -> List[Depositos]:
    """
    Obtiene una lista de todos los registros de Depositos usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, descripcion, codigo, observacion FROM depositos")
        )
        
        depositoss = []
        for row in result.fetchall():
            depositos = Depositos()
            depositos.id = row[0]
            depositos.descripcion = row[1]
            depositos.codigo = row[2]
            depositos.observacion = row[3]
            depositoss.append(depositos)
        
        # No lanzamos excepción si la lista está vacía, simplemente devolvemos la lista vacía
        return depositoss
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Depositos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")
def delete_depositos(db: Session, id: int) -> Depositos:
    """
    Elimina un registro de Depositos por su clave primaria usando SQL directo.
    """
    try:
        # Obtener y eliminar el registro en una sola operación usando OUTPUT
        result = db.execute(
            text("""
                DELETE FROM depositos 
                OUTPUT DELETED.id, DELETED.descripcion, DELETED.codigo, DELETED.observacion
                WHERE id = :id
            """),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depositos no encontrado.")
        
        # Crear el objeto con los datos del registro eliminado
        deleted_depositos = Depositos()
        deleted_depositos.id = result[0]
        deleted_depositos.descripcion = result[1]
        deleted_depositos.codigo = result[2]
        deleted_depositos.observacion = result[3]
        
        db.commit()
        return deleted_depositos
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Depositos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")
def update_depositos(db: Session, id: int, depositos_data: Dict[str, Any]) -> Depositos:
    """
    Actualiza un registro de Depositos por su clave primaria usando SQL directo.
    """
    logger.info(f"Actualizando Depositos con id = {id}")
    try:
        # Verificar que el registro existe
        result = db.execute(
            text("SELECT COUNT(*) FROM depositos WHERE id = :id"),
            {"id": id}
        ).scalar()
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depositos no encontrado.")
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        depositos_data_copy = depositos_data.copy()
        if 'id' in depositos_data_copy:
            del depositos_data_copy['id']
        
        # Si no hay campos para actualizar, obtener el registro actual
        if not depositos_data_copy:
            return get_depositos(db, id)
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in depositos_data_copy:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa con OUTPUT
        query = text(f"""
            UPDATE depositos
            SET {set_clause_str}
            OUTPUT INSERTED.id, INSERTED.descripcion, INSERTED.codigo, INSERTED.observacion
            WHERE id = :id
        """)
        
        # Preparar los parámetros
        params = depositos_data_copy.copy()
        params['id'] = id
        
        # Ejecutar la consulta
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar el Depositos.")
        
        # Crear el objeto con los datos actualizados
        updated_depositos = Depositos()
        updated_depositos.id = result[0]
        updated_depositos.descripcion = result[1]
        updated_depositos.codigo = result[2]
        updated_depositos.observacion = result[3]
        
        return updated_depositos
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Depositos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")
