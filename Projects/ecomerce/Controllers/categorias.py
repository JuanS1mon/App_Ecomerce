from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status, Request
from sqlalchemy import text
from ..models.categorias import EcomerceCategorias as Categorias
from db.models.logs.activity_log import ActivityLog
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

def log_activity(db: Session, user_id: int, action: str, description: str, request: Request):
    """
    Función auxiliar para registrar actividades del usuario en la tabla activity_log.
    Esta función está comentada por defecto y puede activarse según sea necesario.
    """
    # try:
    #     # Obtener IP del cliente
    #     client_ip = request.client.host if request.client else "unknown"
    #     
    #     # Obtener User-Agent
    #     user_agent = request.headers.get("user-agent", "unknown")
    #     
    #     # Crear registro de actividad
    #     activity = ActivityLog(
    #         usuario_id=user_id,
    #         accion=action,
    #         descripcion=description,
    #         ip_address=client_ip,
    #         user_agent=user_agent
    #     )
    #     
    #     db.add(activity)
    #     db.commit()
    #     
    # except Exception as e:
    #     logger.error(f"Error al registrar actividad: {e}")
    #     db.rollback()  # No fallar la operación principal por error de logging

def create_categorias(db: Session, categorias, user_data: dict = None, request: Request = None) -> Categorias:
    """
    Crea un nuevo registro de Categorias en la base de datos usando SQL directo.
    Adaptado para SQL Server usando cláusula OUTPUT.
    ⚠️ Excluye campos autoincrement del INSERT (generados por la BD).
    """
    try:
        # Extraer datos (excluyendo PK autoincrement si aplica)
        if isinstance(categorias, dict):
            categorias_data = categorias
        else:
            categorias_data = {}
            for field in ['nombre', 'descripcion', 'id_padre', 'created_at', 'active']:
                if hasattr(categorias, field):
                    categorias_data[field] = getattr(categorias, field)
        
        # Construir la consulta SQL INSERT con OUTPUT para SQL Server
        # ⚠️ ID autoincrement: se genera automáticamente
        query = text("""
            INSERT INTO ecomerce_categorias (nombre, descripcion, id_padre, created_at, active)
            OUTPUT INSERTED.id, INSERTED.nombre, INSERTED.descripcion, INSERTED.id_padre, INSERTED.created_at, INSERTED.active
            VALUES (:nombre, :descripcion, :id_padre, :created_at, :active)
        """)
        
        # Ejecutar la consulta y obtener el registro insertado directamente
        result = db.execute(query, categorias_data)
        row = result.first()
        db.commit()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El registro no se pudo crear"
            )
        
        # Crear un nuevo objeto Categorias con los valores devueltos
        new_categorias = Categorias()
        new_categorias.id = row[0]
        new_categorias.nombre = row[1]
        new_categorias.descripcion = row[2]
        new_categorias.id_padre = row[3]
        new_categorias.created_at = row[4]
        new_categorias.active = row[5]
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Creó un nuevo registro en Categorias (ID: {new_categorias.id})"
        #         log_activity(db, user_id, "CREATE", description, request)
        
        return new_categorias
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear Categorias: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el registro: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear Categorias: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )
def get_categorias(db: Session, id: int) -> Optional[Categorias]:
    """
    Obtiene un registro de Categorias por su clave primaria usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, nombre, descripcion, id_padre, created_at, active FROM ecomerce_categorias WHERE id = :id"),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categorias no encontrado.")
        
        # Crear el objeto directamente con los valores
        categorias = Categorias()
        categorias.id = result[0]
        categorias.nombre = result[1]
        categorias.descripcion = result[2]
        categorias.id_padre = result[3]
        categorias.created_at = result[4]
        categorias.active = result[5]
        
        return categorias
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Categorias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")
def gets_categorias(db: Session) -> List[Categorias]:
    """
    Obtiene una lista de todos los registros de Categorias usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, nombre, descripcion, id_padre, created_at, active FROM ecomerce_categorias")
        )
        
        categoriass = []
        for row in result.fetchall():
            categorias = Categorias()
            categorias.id = row[0]
            categorias.nombre = row[1]
            categorias.descripcion = row[2]
            categorias.id_padre = row[3]
            categorias.created_at = row[4]
            categorias.active = row[5]
            categoriass.append(categorias)
        
        return categoriass
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Categorias: {e}")
        # En lugar de lanzar HTTPException, devolver lista vacía y loggear el error
        return []
def delete_categorias(db: Session, id: int, user_data: dict = None, request: Request = None) -> Categorias:
    """
    Elimina un registro de Categorias por su clave primaria usando SQL directo.
    """
    try:
        # Obtener y eliminar el registro en una sola operación usando OUTPUT
        result = db.execute(
            text("""
                DELETE FROM ecomerce_categorias 
                OUTPUT DELETED.id, DELETED.nombre, DELETED.descripcion, DELETED.id_padre, DELETED.created_at, DELETED.active
                WHERE id = :id
            """),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categorias no encontrado.")
        
        # Crear el objeto con los datos del registro eliminado
        deleted_categorias = Categorias()
        deleted_categorias.id = result[0]
        deleted_categorias.nombre = result[1]
        deleted_categorias.descripcion = result[2]
        deleted_categorias.id_padre = result[3]
        deleted_categorias.created_at = result[4]
        deleted_categorias.active = result[5]
        
        db.commit()
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Eliminó el registro Categorias (ID: {id})"
        #         log_activity(db, user_id, "DELETE", description, request)
        
        return deleted_categorias
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Categorias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")
def update_categorias(db: Session, id: int, categorias_data: Dict[str, Any], user_data: dict = None, request: Request = None) -> Categorias:
    """
    Actualiza un registro de Categorias por su clave primaria usando SQL directo.
    """
    logger.info(f"Actualizando Categorias con id = {id}")
    try:
        # Verificar que el registro existe
        result = db.execute(
            text("SELECT COUNT(*) FROM ecomerce_categorias WHERE id = :id"),
            {"id": id}
        ).scalar()
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categorias no encontrado.")
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        categorias_data_copy = categorias_data.copy()
        if 'id' in categorias_data_copy:
            del categorias_data_copy['id']
        
        # Si no hay campos para actualizar, obtener el registro actual
        if not categorias_data_copy:
            return get_categorias(db, id)
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in categorias_data_copy:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa con OUTPUT
        query = text(f"""
            UPDATE ecomerce_categorias
            SET {set_clause_str}
            OUTPUT INSERTED.id, INSERTED.nombre, INSERTED.descripcion, INSERTED.id_padre, INSERTED.created_at, INSERTED.active
            WHERE id = :id
        """)
        
        # Preparar los parámetros
        params = categorias_data_copy.copy()
        params['id'] = id
        
        # Ejecutar la consulta
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar el Categorias.")
        
        # Crear el objeto con los datos actualizados
        updated_categorias = Categorias()
        updated_categorias.id = result[0]
        updated_categorias.nombre = result[1]
        updated_categorias.descripcion = result[2]
        updated_categorias.id_padre = result[3]
        updated_categorias.created_at = result[4]
        updated_categorias.active = result[5]
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Actualizó el registro Categorias (ID: {id})"
        #         log_activity(db, user_id, "UPDATE", description, request)
        
        return updated_categorias
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Categorias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")
