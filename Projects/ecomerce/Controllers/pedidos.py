from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status, Request
from sqlalchemy import text
from ..models.pedidos import EcomercePedidos as Pedidos
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

def create_pedidos(db: Session, pedidos, user_data: dict = None, request: Request = None) -> Pedidos:
    """
    Crea un nuevo registro de Pedidos en la base de datos usando SQL directo.
    Adaptado para SQL Server usando cláusula OUTPUT.
    ⚠️ Excluye campos autoincrement del INSERT (generados por la BD).
    """
    try:
        # Extraer datos (excluyendo PK autoincrement si aplica)
        if isinstance(pedidos, dict):
            pedidos_data = pedidos
        else:
            pedidos_data = {}
            for field in ['id_usuario', 'fecha_pedido', 'total', 'estado']:
                if hasattr(pedidos, field):
                    pedidos_data[field] = getattr(pedidos, field)
        
        # Construir la consulta SQL INSERT con OUTPUT para SQL Server
        # ⚠️ ID autoincrement: se genera automáticamente
        query = text("""
            INSERT INTO ecomerce_pedidos (id_usuario, fecha_pedido, total, estado)
            OUTPUT INSERTED.id, INSERTED.id_usuario, INSERTED.fecha_pedido, INSERTED.total, INSERTED.estado
            VALUES (:id_usuario, :fecha_pedido, :total, :estado)
        """)
        
        # Ejecutar la consulta y obtener el registro insertado directamente
        result = db.execute(query, pedidos_data)
        row = result.first()
        db.commit()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El registro no se pudo crear"
            )
        
        # Crear un nuevo objeto Pedidos con los valores devueltos
        new_pedidos = Pedidos()
        new_pedidos.id = row[0]
        new_pedidos.id_usuario = row[1]
        new_pedidos.fecha_pedido = row[2]
        new_pedidos.total = row[3]
        new_pedidos.estado = row[4]
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Creó un nuevo registro en Pedidos (ID: {new_pedidos.id})"
        #         log_activity(db, user_id, "CREATE", description, request)
        
        return new_pedidos
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear Pedidos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el registro: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear Pedidos: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )
def get_pedidos(db: Session, id: int) -> Optional[Pedidos]:
    """
    Obtiene un registro de Pedidos por su clave primaria usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, id_usuario, fecha_pedido, total, estado FROM ecomerce_pedidos WHERE id = :id"),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedidos no encontrado.")
        
        # Crear el objeto directamente con los valores
        pedidos = Pedidos()
        pedidos.id = result[0]
        pedidos.id_usuario = result[1]
        pedidos.fecha_pedido = result[2]
        pedidos.total = result[3]
        pedidos.estado = result[4]
        
        return pedidos
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Pedidos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")
def gets_pedidos(db: Session) -> List[Pedidos]:
    """
    Obtiene una lista de todos los registros de Pedidos usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, id_usuario, fecha_pedido, total, estado FROM ecomerce_pedidos")
        )
        
        pedidoss = []
        for row in result.fetchall():
            pedidos = Pedidos()
            pedidos.id = row[0]
            pedidos.id_usuario = row[1]
            pedidos.fecha_pedido = row[2]
            pedidos.total = row[3]
            pedidos.estado = row[4]
            pedidoss.append(pedidos)
        
        return pedidoss
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Pedidos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")
def delete_pedidos(db: Session, id: int, user_data: dict = None, request: Request = None) -> Pedidos:
    """
    Elimina un registro de Pedidos por su clave primaria usando SQL directo.
    """
    try:
        # Obtener y eliminar el registro en una sola operación usando OUTPUT
        result = db.execute(
            text("""
                DELETE FROM ecomerce_pedidos 
                OUTPUT DELETED.id, DELETED.id_usuario, DELETED.fecha_pedido, DELETED.total, DELETED.estado
                WHERE id = :id
            """),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedidos no encontrado.")
        
        # Crear el objeto con los datos del registro eliminado
        deleted_pedidos = Pedidos()
        deleted_pedidos.id = result[0]
        deleted_pedidos.id_usuario = result[1]
        deleted_pedidos.fecha_pedido = result[2]
        deleted_pedidos.total = result[3]
        deleted_pedidos.estado = result[4]
        
        db.commit()
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Eliminó el registro Pedidos (ID: {id})"
        #         log_activity(db, user_id, "DELETE", description, request)
        
        return deleted_pedidos
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Pedidos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")
def update_pedidos(db: Session, id: int, pedidos_data: Dict[str, Any], user_data: dict = None, request: Request = None) -> Pedidos:
    """
    Actualiza un registro de Pedidos por su clave primaria usando SQL directo.
    """
    logger.info(f"Actualizando Pedidos con id = {id}")
    try:
        # Verificar que el registro existe
        result = db.execute(
            text("SELECT COUNT(*) FROM ecomerce_pedidos WHERE id = :id"),
            {"id": id}
        ).scalar()
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedidos no encontrado.")
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        pedidos_data_copy = pedidos_data.copy()
        if 'id' in pedidos_data_copy:
            del pedidos_data_copy['id']
        
        # Si no hay campos para actualizar, obtener el registro actual
        if not pedidos_data_copy:
            return get_pedidos(db, id)
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in pedidos_data_copy:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa con OUTPUT
        query = text(f"""
            UPDATE ecomerce_pedidos
            SET {set_clause_str}
            OUTPUT INSERTED.id, INSERTED.id_usuario, INSERTED.fecha_pedido, INSERTED.total, INSERTED.estado
            WHERE id = :id
        """)
        
        # Preparar los parámetros
        params = pedidos_data_copy.copy()
        params['id'] = id
        
        # Ejecutar la consulta
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar el Pedidos.")
        
        # Crear el objeto con los datos actualizados
        updated_pedidos = Pedidos()
        updated_pedidos.id = result[0]
        updated_pedidos.id_usuario = result[1]
        updated_pedidos.fecha_pedido = result[2]
        updated_pedidos.total = result[3]
        updated_pedidos.estado = result[4]
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Actualizó el registro Pedidos (ID: {id})"
        #         log_activity(db, user_id, "UPDATE", description, request)
        
        return updated_pedidos
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Pedidos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")
