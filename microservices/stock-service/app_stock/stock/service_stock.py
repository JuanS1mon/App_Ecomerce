# Imports de bibliotecas estándar
from Services.app_stock.stock.model_stock import Stock  # Corregida la importación
from Services.app_stock.stock.model_stock import Stock as StockModel
from datetime import date
from typing import List, Optional, Dict, Any
import logging

# Imports de terceros
from fastapi import HTTPException, status
from sqlalchemy import text,func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
def anular_movimiento(db: Session, nro_movimiento: int) -> int:
    """
    Anula todos los registros de un movimiento de stock.
    """
    try:
        result = db.execute(
            text("""
                UPDATE stock
                SET anulado = 1
                WHERE nro_movimiento = :nro_movimiento
            """),
            {"nro_movimiento": nro_movimiento}
        )
        db.commit()
        return result.rowcount
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al anular movimiento {nro_movimiento}: {e}")
        raise HTTPException(status_code=500, detail="Error al anular el movimiento")

def create_stock(db: Session, stock_origen: Stock, stock_destino: Stock) -> List[Stock]:
    try:
        insert_query = text("""
            INSERT INTO stock (
                nro_movimiento, codigo_art, id_articulos_serie, id_deposito,
                cant_disponible, cant_reservado, cant_preparado, tipo, fecha, observacion
            )
            OUTPUT INSERTED.id, INSERTED.nro_movimiento, INSERTED.codigo_art
            VALUES (
                :nro_movimiento, :codigo_art, :id_articulos_serie, :id_deposito,
                :cant_disponible, :cant_reservado, :cant_preparado, :tipo, :fecha, :observacion
            )
        """)

        def to_dict(stock):
            return {
                "nro_movimiento": stock.nro_movimiento,
                "codigo_art": stock.codigo_art,
                "id_articulos_serie": stock.id_articulos_serie,
                "id_deposito": stock.id_deposito,
                "cant_disponible": stock.cant_disponible,
                "cant_reservado": stock.cant_reservado,
                "cant_preparado": stock.cant_preparado,
                "tipo": stock.tipo,
                "fecha": stock.fecha,
                "observacion": stock.observacion
            }

        inserted_origen = db.execute(insert_query, to_dict(stock_origen)).first()
        stock_origen.id = inserted_origen[0]

        inserted_destino = db.execute(insert_query, to_dict(stock_destino)).first()
        stock_destino.id = inserted_destino[0]

        db.commit()

        # Recargar datos completos desde la base
        query = text("SELECT * FROM stock WHERE id IN (:id1, :id2)")
        result = db.execute(query, {"id1": stock_origen.id, "id2": stock_destino.id}).mappings().fetchall()

        return result  # Devuelve registros como diccionarios completos



    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error en create_stock: {e}")
        raise HTTPException(status_code=500, detail="Error al crear registros de stock")



def get_stock(db: Session, id: int) -> Optional[Stock]:
    """
    Obtiene un registro de Stock por su clave primaria usando SQL directo.
    """
    try:
        # Consulta modificada para incluir solo los campos que existen
        result = db.execute(
            text("SELECT * FROM stock WHERE id = :id"),
                {"id": id}
            ).mappings().first()

        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock no encontrado.")
        
        # Crear el objeto directamente con los valores
        stock = Stock()
        stock.id = result['id']
        stock.nro_movimiento = result['nro_movimiento']
        stock.codigo_art = result['codigo_art']
        stock.id_articulos_serie = result['id_articulos_serie']
        stock.id_deposito = result['id_deposito']
        stock.cant_disponible = result['cant_disponible']
        stock.cant_reservado = result['cant_reservado']
        stock.cant_preparado = result['cant_preparado']
        stock.tipo = result['tipo']
        stock.fecha = result['fecha'].isoformat() if result['fecha'] else ""

        stock.observacion = result['observacion']
        stock.anulado = result['anulado']


        
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
            text("SELECT id, nro_movimiento, codigo_art, id_articulos_serie, id_deposito, cant_disponible, cant_reservado, cant_preparado, tipo, fecha, observacion, anulado FROM stock")
        ).mappings().all()

        
        stocks = []
        for row in result:
            stock = Stock()
            stock.id = row['id']
            stock.nro_movimiento = row['nro_movimiento']
            stock.codigo_art = row['codigo_art']
            stock.id_articulos_serie = row['id_articulos_serie']
            stock.id_deposito = row['id_deposito']
            stock.cant_disponible = row['cant_disponible']
            stock.cant_reservado = row['cant_reservado']
            stock.cant_preparado = row['cant_preparado']
            stock.tipo = row['tipo']
            stock.fecha = row['fecha']
            stock.observacion = row['observacion']
            stock.anulado = row['anulado']

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
        valid_fields = ['nro_movimiento', 'codigo_art', 'id_articulos_serie', 'id_deposito', 'cant_disponible', 'cant_reservado', 'cant_preparado', 'tipo', 'fecha', 'observacion']

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
