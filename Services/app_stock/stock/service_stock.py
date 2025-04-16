from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from sqlalchemy import text
from .model_stock import Stock  # Corregida la importación
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

def create_stock(db: Session, stock: Stock) -> Stock:
    """
    Crea un nuevo registro de Stock en la base de datos usando SQL directo.
    Adaptado para SQL Server usando cláusula OUTPUT.
    """
    try:
        # Preparar los datos para la consulta, usando solo los campos que existen en la tabla
        stock_data = {}
        
        for field in ['id', 'nro_movimiento', 'codigo_art']:
            if hasattr(stock, field):
                stock_data[field] = getattr(stock, field)
        
        # Construir la consulta SQL INSERT con OUTPUT para SQL Server
        query = text("""
            INSERT INTO stock (id, nro_movimiento, codigo_art)
            OUTPUT INSERTED.id, INSERTED.nro_movimiento, INSERTED.codigo_art
            VALUES (:id, :nro_movimiento, :codigo_art)
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
        new_stock.nro_movimiento = row[1]
        new_stock.codigo_art = row[2]
        # Establecer valores predeterminados para los campos no presentes en la tabla
        new_stock.id_articulos_serie = 0
        new_stock.id_deposito = 0
        new_stock.cant_disponible = 0.0
        new_stock.cant_reservado = 0.0
        new_stock.cant_preparado = 0.0
        new_stock.tipo = False
        new_stock.fecha = ""
        new_stock.observacion = ""
        
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
        # Consulta modificada para incluir solo los campos que existen
        result = db.execute(
            text("SELECT id, nro_movimiento, codigo_art FROM stock WHERE id = :id"),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock no encontrado.")
        
        # Crear el objeto directamente con los valores
        stock = Stock()
        stock.id = result[0]
        stock.nro_movimiento = result[1]
        stock.codigo_art = result[2]
        # Establecer valores predeterminados para los campos no presentes en la tabla
        stock.id_articulos_serie = 0
        stock.id_deposito = 0
        stock.cant_disponible = 0.0
        stock.cant_reservado = 0.0
        stock.cant_preparado = 0.0
        stock.tipo = False
        stock.fecha = ""
        stock.observacion = ""
        
        return stock
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")

def gets_stock(db: Session) -> List[Stock]:
    """
    Obtiene una lista de todos los registros de Stock usando SQL directo.
    """
    try:
        # Consulta modificada para incluir solo los campos que existen en la tabla
        result = db.execute(
            text("SELECT id, nro_movimiento, codigo_art FROM stock")
        )
        
        stocks = []
        for row in result.fetchall():
            stock = Stock()
            stock.id = row[0]
            stock.nro_movimiento = row[1]
            stock.codigo_art = row[2]
            # Establecer valores predeterminados para los campos no presentes en la tabla
            stock.id_articulos_serie = 0
            stock.id_deposito = 0
            stock.cant_disponible = 0.0
            stock.cant_reservado = 0.0
            stock.cant_preparado = 0.0
            stock.tipo = False
            stock.fecha = ""
            stock.observacion = ""
            stocks.append(stock)
        
        return stocks
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")

def delete_stock(db: Session, id: int) -> Stock:
    """
    Elimina un registro de Stock por su clave primaria usando SQL directo.
    """
    try:
        # Obtener y eliminar el registro en una sola operación usando OUTPUT
        result = db.execute(
            text("""
                DELETE FROM stock 
                OUTPUT DELETED.id, DELETED.nro_movimiento, DELETED.codigo_art
                WHERE id = :id
            """),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock no encontrado.")
        
        # Crear el objeto con los datos del registro eliminado
        deleted_stock = Stock()
        deleted_stock.id = result[0]
        deleted_stock.nro_movimiento = result[1]
        deleted_stock.codigo_art = result[2]
        # Establecer valores predeterminados para los campos no presentes en la tabla
        deleted_stock.id_articulos_serie = 0
        deleted_stock.id_deposito = 0
        deleted_stock.cant_disponible = 0.0
        deleted_stock.cant_reservado = 0.0
        deleted_stock.cant_preparado = 0.0
        deleted_stock.tipo = False
        deleted_stock.fecha = ""
        deleted_stock.observacion = ""
        
        db.commit()
        return deleted_stock
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")

def update_stock(db: Session, id: int, stock_data: Dict[str, Any]) -> Stock:
    """
    Actualiza un registro de Stock por su clave primaria usando SQL directo.
    """
    logger.info(f"Actualizando Stock con id = {id}")
    try:
        # Verificar que el registro existe
        result = db.execute(
            text("SELECT COUNT(*) FROM stock WHERE id = :id"),
            {"id": id}
        ).scalar()
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock no encontrado.")
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        stock_data_copy = stock_data.copy()
        if 'id' in stock_data_copy:
            del stock_data_copy['id']
        
        # Filtrar los campos que no existen en la tabla
        valid_fields = ['nro_movimiento', 'codigo_art']
        filtered_data = {k: v for k, v in stock_data_copy.items() if k in valid_fields}
        
        # Si no hay campos para actualizar, obtener el registro actual
        if not filtered_data:
            return get_stock(db, id)
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in filtered_data:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa con OUTPUT
        query = text(f"""
            UPDATE stock
            SET {set_clause_str}
            OUTPUT INSERTED.id, INSERTED.nro_movimiento, INSERTED.codigo_art
            WHERE id = :id
        """)
        
        # Preparar los parámetros
        params = filtered_data.copy()
        params['id'] = id
        
        # Ejecutar la consulta
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar el Stock.")
        
        # Crear el objeto con los datos actualizados
        updated_stock = Stock()
        updated_stock.id = result[0]
        updated_stock.nro_movimiento = result[1]
        updated_stock.codigo_art = result[2]
        # Establecer valores predeterminados para los campos no presentes en la tabla
        updated_stock.id_articulos_serie = 0
        updated_stock.id_deposito = 0
        updated_stock.cant_disponible = 0.0
        updated_stock.cant_reservado = 0.0
        updated_stock.cant_preparado = 0.0
        updated_stock.tipo = False
        updated_stock.fecha = ""
        updated_stock.observacion = ""
        
        return updated_stock
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")
