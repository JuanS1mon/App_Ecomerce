from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status, Request
from sqlalchemy import text
from ..models.carritos import EcomerceCarritos as Carritos
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

def create_carritos(db: Session, carritos, user_data: dict = None, request: Request = None) -> Carritos:
    """
    Crea un nuevo registro de Carritos en la base de datos usando SQL directo.
    Adaptado para SQL Server usando cláusula OUTPUT.
    ⚠️ Excluye campos autoincrement del INSERT (generados por la BD).
    """
    try:
        # Extraer datos (excluyendo PK autoincrement si aplica)
        if isinstance(carritos, dict):
            carritos_data = carritos
        else:
            carritos_data = {}
            for field in ['id_usuario', 'estado', 'created_at']:
                if hasattr(carritos, field):
                    carritos_data[field] = getattr(carritos, field)
        
        # Construir la consulta SQL INSERT con OUTPUT para SQL Server
        # ⚠️ ID autoincrement: se genera automáticamente
        query = text("""
            INSERT INTO ecomerce_carritos (id_usuario, estado, created_at)
            OUTPUT INSERTED.id, INSERTED.id_usuario, INSERTED.estado, INSERTED.created_at
            VALUES (:id_usuario, :estado, :created_at)
        """)
        
        # Ejecutar la consulta y obtener el registro insertado directamente
        result = db.execute(query, carritos_data)
        row = result.first()
        db.commit()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El registro no se pudo crear"
            )
        
        # Crear un nuevo objeto Carritos con los valores devueltos
        new_carritos = Carritos()
        new_carritos.id = row[0]
        new_carritos.id_usuario = row[1]
        new_carritos.estado = row[2]
        new_carritos.created_at = row[3]
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Creó un nuevo registro en Carritos (ID: {new_carritos.id})"
        #         log_activity(db, user_id, "CREATE", description, request)
        
        return new_carritos
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear Carritos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el registro: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear Carritos: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )
def get_carritos(db: Session, id: int) -> Optional[Carritos]:
    """
    Obtiene un registro de Carritos por su clave primaria usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, id_usuario, estado, created_at FROM ecomerce_carritos WHERE id = :id"),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carritos no encontrado.")
        
        # Crear el objeto directamente con los valores
        carritos = Carritos()
        carritos.id = result[0]
        carritos.id_usuario = result[1]
        carritos.estado = result[2]
        carritos.created_at = result[3]
        
        return carritos
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Carritos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")
def gets_carritos(db: Session) -> List[Carritos]:
    """
    Obtiene una lista de todos los registros de Carritos usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, id_usuario, estado, created_at FROM ecomerce_carritos")
        )
        
        carritoss = []
        for row in result.fetchall():
            carritos = Carritos()
            carritos.id = row[0]
            carritos.id_usuario = row[1]
            carritos.estado = row[2]
            carritos.created_at = row[3]
            carritoss.append(carritos)
        
        return carritoss
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Carritos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")
def delete_carritos(db: Session, id: int, user_data: dict = None, request: Request = None) -> Carritos:
    """
    Elimina un registro de Carritos por su clave primaria usando SQL directo.
    """
    try:
        # Obtener y eliminar el registro en una sola operación usando OUTPUT
        result = db.execute(
            text("""
                DELETE FROM ecomerce_carritos 
                OUTPUT DELETED.id, DELETED.id_usuario, DELETED.estado, DELETED.created_at
                WHERE id = :id
            """),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carritos no encontrado.")
        
        # Crear el objeto con los datos del registro eliminado
        deleted_carritos = Carritos()
        deleted_carritos.id = result[0]
        deleted_carritos.id_usuario = result[1]
        deleted_carritos.estado = result[2]
        deleted_carritos.created_at = result[3]
        
        db.commit()
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Eliminó el registro Carritos (ID: {id})"
        #         log_activity(db, user_id, "DELETE", description, request)
        
        return deleted_carritos
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Carritos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")
def update_carritos(db: Session, id: int, carritos_data: Dict[str, Any], user_data: dict = None, request: Request = None) -> Carritos:
    """
    Actualiza un registro de Carritos por su clave primaria usando SQL directo.
    """
    logger.info(f"Actualizando Carritos con id = {id}")
    try:
        # Verificar que el registro existe
        result = db.execute(
            text("SELECT COUNT(*) FROM ecomerce_carritos WHERE id = :id"),
            {"id": id}
        ).scalar()
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carritos no encontrado.")
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        carritos_data_copy = carritos_data.copy()
        if 'id' in carritos_data_copy:
            del carritos_data_copy['id']
        
        # Si no hay campos para actualizar, obtener el registro actual
        if not carritos_data_copy:
            return get_carritos(db, id)
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in carritos_data_copy:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa con OUTPUT
        query = text(f"""
            UPDATE ecomerce_carritos
            SET {set_clause_str}
            OUTPUT INSERTED.id, INSERTED.id_usuario, INSERTED.estado, INSERTED.created_at
            WHERE id = :id
        """)
        
        # Preparar los parámetros
        params = carritos_data_copy.copy()
        params['id'] = id
        
        # Ejecutar la consulta
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar el Carritos.")
        
        # Crear el objeto con los datos actualizados
        updated_carritos = Carritos()
        updated_carritos.id = result[0]
        updated_carritos.id_usuario = result[1]
        updated_carritos.estado = result[2]
        updated_carritos.created_at = result[3]
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Actualizó el registro Carritos (ID: {id})"
        #         log_activity(db, user_id, "UPDATE", description, request)
        
        return updated_carritos
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Carritos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")
