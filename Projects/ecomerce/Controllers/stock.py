from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status, Request
from sqlalchemy import text
from ..models.stock import EcomerceStock as Stock
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

def create_stock(db: Session, stock, user_data: dict = None, request: Request = None) -> Stock:
    """
    Crea un nuevo registro de Stock en la base de datos usando SQL directo.
    Adaptado para SQL Server usando cláusula OUTPUT.
    ⚠️ Excluye campos autoincrement del INSERT (generados por la BD).
    """
    try:
        # Extraer datos (excluyendo PK autoincrement si aplica)
        if isinstance(stock, dict):
            stock_data = stock
        else:
            stock_data = {}
            for field in ['id_producto', 'cantidad_disponible', 'cantidad_reservada', 'ubicacion', 'updated_at']:
                if hasattr(stock, field):
                    stock_data[field] = getattr(stock, field)
        
        # Construir la consulta SQL INSERT con OUTPUT para SQL Server
        # ⚠️ ID autoincrement: se genera automáticamente
        query = text("""
            INSERT INTO ecomerce_stock (id_producto, cantidad_disponible, cantidad_reservada, ubicacion, updated_at)
            OUTPUT INSERTED.id, INSERTED.id_producto, INSERTED.cantidad_disponible, INSERTED.cantidad_reservada, INSERTED.ubicacion, INSERTED.updated_at
            VALUES (:id_producto, :cantidad_disponible, :cantidad_reservada, :ubicacion, :updated_at)
        """)
        
        # Ejecutar la consulta y obtener el registro insertado directamente
        result = db.execute(query, stock_data)
        row = result.first()
        db.commit()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El registro no se pudo crear"
            )
        
        # Crear un nuevo objeto Stock con los valores devueltos
        new_stock = Stock()
        new_stock.id = row[0]
        new_stock.id_producto = row[1]
        new_stock.cantidad_disponible = row[2]
        new_stock.cantidad_reservada = row[3]
        new_stock.ubicacion = row[4]
        new_stock.updated_at = row[5]
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Creó un nuevo registro en Stock (ID: {new_stock.id})"
        #         log_activity(db, user_id, "CREATE", description, request)
        
        return new_stock
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear Stock: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el registro: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear Stock: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )
def get_stock(db: Session, id: int) -> Optional[Stock]:
    """
    Obtiene un registro de Stock por su clave primaria usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, id_producto, cantidad_disponible, cantidad_reservada, ubicacion, updated_at FROM ecomerce_stock WHERE id = :id"),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock no encontrado.")
        
        # Crear el objeto directamente con los valores
        stock = Stock()
        stock.id = result[0]
        stock.id_producto = result[1]
        stock.cantidad_disponible = result[2]
        stock.cantidad_reservada = result[3]
        stock.ubicacion = result[4]
        stock.updated_at = result[5]
        
        return stock
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")
def gets_stock(db: Session) -> List[Stock]:
    """
    Obtiene una lista de todos los registros de Stock usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, id_producto, cantidad_disponible, cantidad_reservada, ubicacion, updated_at FROM ecomerce_stock")
        )
        
        stocks = []
        for row in result.fetchall():
            stock = Stock()
            stock.id = row[0]
            stock.id_producto = row[1]
            stock.cantidad_disponible = row[2]
            stock.cantidad_reservada = row[3]
            stock.ubicacion = row[4]
            stock.updated_at = row[5]
            stocks.append(stock)
        
        return stocks
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")
def delete_stock(db: Session, id: int, user_data: dict = None, request: Request = None) -> Stock:
    """
    Elimina un registro de Stock por su clave primaria usando SQL directo.
    """
    try:
        # Obtener y eliminar el registro en una sola operación usando OUTPUT
        result = db.execute(
            text("""
                DELETE FROM ecomerce_stock 
                OUTPUT DELETED.id, DELETED.id_producto, DELETED.cantidad_disponible, DELETED.cantidad_reservada, DELETED.ubicacion, DELETED.updated_at
                WHERE id = :id
            """),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock no encontrado.")
        
        # Crear el objeto con los datos del registro eliminado
        deleted_stock = Stock()
        deleted_stock.id = result[0]
        deleted_stock.id_producto = result[1]
        deleted_stock.cantidad_disponible = result[2]
        deleted_stock.cantidad_reservada = result[3]
        deleted_stock.ubicacion = result[4]
        deleted_stock.updated_at = result[5]
        
        db.commit()
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Eliminó el registro Stock (ID: {id})"
        #         log_activity(db, user_id, "DELETE", description, request)
        
        return deleted_stock
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")
def update_stock(db: Session, id: int, stock_data: Dict[str, Any], user_data: dict = None, request: Request = None) -> Stock:
    """
    Actualiza un registro de Stock por su clave primaria usando SQL directo.
    """
    logger.info(f"Actualizando Stock con id = {id}")
    try:
        # Verificar que el registro existe
        result = db.execute(
            text("SELECT COUNT(*) FROM ecomerce_stock WHERE id = :id"),
            {"id": id}
        ).scalar()
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock no encontrado.")
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        stock_data_copy = stock_data.copy()
        if 'id' in stock_data_copy:
            del stock_data_copy['id']
        
        # Si no hay campos para actualizar, obtener el registro actual
        if not stock_data_copy:
            return get_stock(db, id)
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in stock_data_copy:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa con OUTPUT
        query = text(f"""
            UPDATE ecomerce_stock
            SET {set_clause_str}
            OUTPUT INSERTED.id, INSERTED.id_producto, INSERTED.cantidad_disponible, INSERTED.cantidad_reservada, INSERTED.ubicacion, INSERTED.updated_at
            WHERE id = :id
        """)
        
        # Preparar los parámetros
        params = stock_data_copy.copy()
        params['id'] = id
        
        # Ejecutar la consulta
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar el Stock.")
        
        # Crear el objeto con los datos actualizados
        updated_stock = Stock()
        updated_stock.id = result[0]
        updated_stock.id_producto = result[1]
        updated_stock.cantidad_disponible = result[2]
        updated_stock.cantidad_reservada = result[3]
        updated_stock.ubicacion = result[4]
        updated_stock.updated_at = result[5]
        
        # Logging opcional de actividad (comentado por defecto)
        # if user_data and request:
        #     user_id = user_data.get("user", {}).get("codigo")
        #     if user_id:
        #         description = f"Actualizó el registro Stock (ID: {id})"
        #         log_activity(db, user_id, "UPDATE", description, request)
        
        return updated_stock
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")
