from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status, Request
from sqlalchemy import text
from ..models.carrito_items import EcomerceCarrito_items as Carrito_items
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

def create_carrito_items(db: Session, carrito_items, user_data: dict = None, request: Request = None) -> Carrito_items:
    """
    Crea un nuevo registro de Carrito_items en la base de datos usando SQL directo.
    Adaptado para SQL Server usando cláusula OUTPUT.
    ⚠️ Excluye campos autoincrement del INSERT (generados por la BD).
    """
    try:
        # Extraer datos (excluyendo PK autoincrement si aplica)
        if isinstance(carrito_items, dict):
            carrito_items_data = carrito_items
        else:
            carrito_items_data = {}
            for field in ['id_carrito', 'id_producto', 'cantidad', 'precio_unitario']:
                if hasattr(carrito_items, field):
                    carrito_items_data[field] = getattr(carrito_items, field)
        
        # Construir la consulta SQL INSERT con OUTPUT para SQL Server
        # ⚠️ ID autoincrement: se genera automáticamente
        query = text("""
            INSERT INTO ecomerce_carrito_items (id_carrito, id_producto, cantidad, precio_unitario)
            OUTPUT INSERTED.id, INSERTED.id_carrito, INSERTED.id_producto, INSERTED.cantidad, INSERTED.precio_unitario
            VALUES (:id_carrito, :id_producto, :cantidad, :precio_unitario)
        """)
        
        # Ejecutar la consulta y obtener el registro insertado directamente
        result = db.execute(query, carrito_items_data)
        row = result.first()
        db.commit()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El registro no se pudo crear"
            )
        
        # Crear un nuevo objeto Carrito_items con los valores devueltos
        new_carrito_items = Carrito_items()
        new_carrito_items.id = row[0]
        new_carrito_items.id_carrito = row[1]
        new_carrito_items.id_producto = row[2]
        new_carrito_items.cantidad = row[3]
        new_carrito_items.precio_unitario = row[4]
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Creó un nuevo registro en Carrito_items (ID: {new_carrito_items.id})"
        #         log_activity(db, user_id, "CREATE", description, request)
        
        return new_carrito_items
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear Carrito_items: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el registro: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear Carrito_items: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )
def get_carrito_items(db: Session, id: int) -> Optional[Carrito_items]:
    """
    Obtiene un registro de Carrito_items por su clave primaria usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, id_carrito, id_producto, cantidad, precio_unitario FROM ecomerce_carrito_items WHERE id = :id"),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito_items no encontrado.")
        
        # Crear el objeto directamente con los valores
        carrito_items = Carrito_items()
        carrito_items.id = result[0]
        carrito_items.id_carrito = result[1]
        carrito_items.id_producto = result[2]
        carrito_items.cantidad = result[3]
        carrito_items.precio_unitario = result[4]
        
        return carrito_items
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Carrito_items: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")
def gets_carrito_items(db: Session) -> List[Carrito_items]:
    """
    Obtiene una lista de todos los registros de Carrito_items usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, id_carrito, id_producto, cantidad, precio_unitario FROM ecomerce_carrito_items")
        )
        
        carrito_itemss = []
        for row in result.fetchall():
            carrito_items = Carrito_items()
            carrito_items.id = row[0]
            carrito_items.id_carrito = row[1]
            carrito_items.id_producto = row[2]
            carrito_items.cantidad = row[3]
            carrito_items.precio_unitario = row[4]
            carrito_itemss.append(carrito_items)
        
        return carrito_itemss
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Carrito_items: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")
def delete_carrito_items(db: Session, id: int, user_data: dict = None, request: Request = None) -> Carrito_items:
    """
    Elimina un registro de Carrito_items por su clave primaria usando SQL directo.
    """
    try:
        # Obtener y eliminar el registro en una sola operación usando OUTPUT
        result = db.execute(
            text("""
                DELETE FROM ecomerce_carrito_items 
                OUTPUT DELETED.id, DELETED.id_carrito, DELETED.id_producto, DELETED.cantidad, DELETED.precio_unitario
                WHERE id = :id
            """),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito_items no encontrado.")
        
        # Crear el objeto con los datos del registro eliminado
        deleted_carrito_items = Carrito_items()
        deleted_carrito_items.id = result[0]
        deleted_carrito_items.id_carrito = result[1]
        deleted_carrito_items.id_producto = result[2]
        deleted_carrito_items.cantidad = result[3]
        deleted_carrito_items.precio_unitario = result[4]
        
        db.commit()
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Eliminó el registro Carrito_items (ID: {id})"
        #         log_activity(db, user_id, "DELETE", description, request)
        
        return deleted_carrito_items
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Carrito_items: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")
def update_carrito_items(db: Session, id: int, carrito_items_data: Dict[str, Any], user_data: dict = None, request: Request = None) -> Carrito_items:
    """
    Actualiza un registro de Carrito_items por su clave primaria usando SQL directo.
    """
    logger.info(f"Actualizando Carrito_items con id = {id}")
    try:
        # Verificar que el registro existe
        result = db.execute(
            text("SELECT COUNT(*) FROM ecomerce_carrito_items WHERE id = :id"),
            {"id": id}
        ).scalar()
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito_items no encontrado.")
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        carrito_items_data_copy = carrito_items_data.copy()
        if 'id' in carrito_items_data_copy:
            del carrito_items_data_copy['id']
        
        # Si no hay campos para actualizar, obtener el registro actual
        if not carrito_items_data_copy:
            return get_carrito_items(db, id)
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in carrito_items_data_copy:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa con OUTPUT
        query = text(f"""
            UPDATE ecomerce_carrito_items
            SET {set_clause_str}
            OUTPUT INSERTED.id, INSERTED.id_carrito, INSERTED.id_producto, INSERTED.cantidad, INSERTED.precio_unitario
            WHERE id = :id
        """)
        
        # Preparar los parámetros
        params = carrito_items_data_copy.copy()
        params['id'] = id
        
        # Ejecutar la consulta
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar el Carrito_items.")
        
        # Crear el objeto con los datos actualizados
        updated_carrito_items = Carrito_items()
        updated_carrito_items.id = result[0]
        updated_carrito_items.id_carrito = result[1]
        updated_carrito_items.id_producto = result[2]
        updated_carrito_items.cantidad = result[3]
        updated_carrito_items.precio_unitario = result[4]
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Actualizó el registro Carrito_items (ID: {id})"
        #         log_activity(db, user_id, "UPDATE", description, request)
        
        return updated_carrito_items
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Carrito_items: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")
