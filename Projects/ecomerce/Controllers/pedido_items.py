from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status, Request
from sqlalchemy import text
from ..models.pedido_items import EcomercePedidoItems as PedidoItems
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
    #     client_ip = request.client.host if request.client else "unknown"
    #     user_agent = request.headers.get("user-agent", "unknown")
    #     activity = ActivityLog(
    #         usuario_id=user_id,
    #         accion=action,
    #         descripcion=description,
    #         ip_address=client_ip,
    #         user_agent=user_agent
    #     )
    #     db.add(activity)
    #     db.commit()
    # except Exception as e:
    #     logger.error(f"Error al registrar actividad: {e}")
    #     db.rollback()

def create_pedido_items(db: Session, pedido_items, user_data: dict = None, request: Request = None) -> PedidoItems:
    """
    Crea un nuevo registro de PedidoItems en la base de datos usando SQL directo.
    """
    try:
        if isinstance(pedido_items, dict):
            pedido_items_data = pedido_items
        else:
            pedido_items_data = {}
            for field in ['id_pedido', 'id_producto', 'cantidad', 'precio_unitario', 'nombre_producto']:
                if hasattr(pedido_items, field):
                    pedido_items_data[field] = getattr(pedido_items, field)
        
        query = text("""
            INSERT INTO ecomerce_pedido_items (id_pedido, id_producto, cantidad, precio_unitario, nombre_producto)
            OUTPUT INSERTED.id, INSERTED.id_pedido, INSERTED.id_producto, INSERTED.cantidad, INSERTED.precio_unitario, INSERTED.nombre_producto, INSERTED.created_at, INSERTED.updated_at
            VALUES (:id_pedido, :id_producto, :cantidad, :precio_unitario, :nombre_producto)
        """)
        
        result = db.execute(query, pedido_items_data)
        row = result.first()
        db.commit()
        
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El registro no se pudo crear")
        
        new_pedido_items = PedidoItems()
        new_pedido_items.id = row[0]
        new_pedido_items.id_pedido = row[1]
        new_pedido_items.id_producto = row[2]
        new_pedido_items.cantidad = row[3]
        new_pedido_items.precio_unitario = row[4]
        new_pedido_items.nombre_producto = row[5]
        new_pedido_items.created_at = row[6]
        new_pedido_items.updated_at = row[7]
        
        return new_pedido_items
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear PedidoItems: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear el registro: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear PedidoItems: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error inesperado: {str(e)}")

def get_pedido_items(db: Session, id: int) -> Optional[PedidoItems]:
    """
    Obtiene un registro de PedidoItems por su clave primaria.
    """
    try:
        result = db.execute(text("""
            SELECT id, id_pedido, id_producto, cantidad, precio_unitario, nombre_producto, created_at, updated_at
            FROM ecomerce_pedido_items WHERE id = :id
        """), {"id": id}).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PedidoItems no encontrado.")
        
        pedido_items = PedidoItems()
        pedido_items.id = result[0]
        pedido_items.id_pedido = result[1]
        pedido_items.id_producto = result[2]
        pedido_items.cantidad = result[3]
        pedido_items.precio_unitario = result[4]
        pedido_items.nombre_producto = result[5]
        pedido_items.created_at = result[6]
        pedido_items.updated_at = result[7]
        
        return pedido_items
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener PedidoItems: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")

def gets_pedido_items(db: Session) -> List[PedidoItems]:
    """
    Obtiene una lista de todos los registros de PedidoItems.
    """
    try:
        result = db.execute(text("""
            SELECT id, id_pedido, id_producto, cantidad, precio_unitario, nombre_producto, created_at, updated_at
            FROM ecomerce_pedido_items
        """))
        
        pedido_itemss = []
        for row in result.fetchall():
            pedido_items = PedidoItems()
            pedido_items.id = row[0]
            pedido_items.id_pedido = row[1]
            pedido_items.id_producto = row[2]
            pedido_items.cantidad = row[3]
            pedido_items.precio_unitario = row[4]
            pedido_items.nombre_producto = row[5]
            pedido_items.created_at = row[6]
            pedido_items.updated_at = row[7]
            pedido_itemss.append(pedido_items)
        
        return pedido_itemss
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de PedidoItems: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")

def delete_pedido_items(db: Session, id: int, user_data: dict = None, request: Request = None) -> PedidoItems:
    """
    Elimina un registro de PedidoItems.
    """
    try:
        result = db.execute(text("""
            DELETE FROM ecomerce_pedido_items 
            OUTPUT DELETED.id, DELETED.id_pedido, DELETED.id_producto, DELETED.cantidad, DELETED.precio_unitario, DELETED.nombre_producto, DELETED.created_at, DELETED.updated_at
            WHERE id = :id
        """), {"id": id}).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PedidoItems no encontrado.")
        
        deleted_pedido_items = PedidoItems()
        deleted_pedido_items.id = result[0]
        deleted_pedido_items.id_pedido = result[1]
        deleted_pedido_items.id_producto = result[2]
        deleted_pedido_items.cantidad = result[3]
        deleted_pedido_items.precio_unitario = result[4]
        deleted_pedido_items.nombre_producto = result[5]
        deleted_pedido_items.created_at = result[6]
        deleted_pedido_items.updated_at = result[7]
        
        db.commit()
        
        return deleted_pedido_items
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar PedidoItems: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")

def update_pedido_items(db: Session, id: int, pedido_items_data: Dict[str, Any], user_data: dict = None, request: Request = None) -> PedidoItems:
    """
    Actualiza un registro de PedidoItems.
    """
    logger.info(f"Actualizando PedidoItems con id = {id}")
    try:
        result = db.execute(text("SELECT COUNT(*) FROM ecomerce_pedido_items WHERE id = :id"), {"id": id}).scalar()
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PedidoItems no encontrado.")
        
        pedido_items_data_copy = pedido_items_data.copy()
        if 'id' in pedido_items_data_copy:
            del pedido_items_data_copy['id']
        
        if not pedido_items_data_copy:
            return get_pedido_items(db, id)
        
        set_clauses = []
        for field in pedido_items_data_copy:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        query = text(f"""
            UPDATE ecomerce_pedido_items
            SET {set_clause_str}
            OUTPUT INSERTED.id, INSERTED.id_pedido, INSERTED.id_producto, INSERTED.cantidad, INSERTED.precio_unitario, INSERTED.nombre_producto, INSERTED.created_at, INSERTED.updated_at
            WHERE id = :id
        """)
        
        params = pedido_items_data_copy.copy()
        params['id'] = id
        
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar el PedidoItems.")
        
        updated_pedido_items = PedidoItems()
        updated_pedido_items.id = result[0]
        updated_pedido_items.id_pedido = result[1]
        updated_pedido_items.id_producto = result[2]
        updated_pedido_items.cantidad = result[3]
        updated_pedido_items.precio_unitario = result[4]
        updated_pedido_items.nombre_producto = result[5]
        updated_pedido_items.created_at = result[6]
        updated_pedido_items.updated_at = result[7]
        
        return updated_pedido_items
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar PedidoItems: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")