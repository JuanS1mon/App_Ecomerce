# Imports de bibliotecas estándar
from sql_app.Services.app_stock.stock_historico.model_stock_historico import Stock_historico  # Corregida la importación
from typing import List, Optional, Dict, Any
import logging

# Imports de terceros
from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def create_stock_historico(db: Session, stock_historico: Stock_historico) -> Stock_historico:
    """
    Crea un nuevo registro de Stock_historico en la base de datos usando SQL directo.
    Adaptado para SQL Server usando cláusula OUTPUT.
    """
    try:
        # Preparar los datos para la consulta
        stock_historico_data = {}
        
        for field in ['id', 'nro_movimiento', 'codigo_art', 'id_articulos_serie', 'id_deposito', 'cant_disponible', 'cant_reservado', 'cant_preparado', 'tipo', 'fecha', 'observacion']:
            if hasattr(stock_historico, field):
                stock_historico_data[field] = getattr(stock_historico, field)
        
        # Construir la consulta SQL INSERT con OUTPUT para SQL Server
        query = text("""
            INSERT INTO stock_historico (id, nro_movimiento, codigo_art, id_articulos_serie, id_deposito, cant_disponible, cant_reservado, cant_preparado, tipo, fecha, observacion)
            OUTPUT INSERTED.id, INSERTED.nro_movimiento, INSERTED.codigo_art, INSERTED.id_articulos_serie, INSERTED.id_deposito, INSERTED.cant_disponible, INSERTED.cant_reservado, INSERTED.cant_preparado, INSERTED.tipo, INSERTED.fecha, INSERTED.observacion
            VALUES (:id, :nro_movimiento, :codigo_art, :id_articulos_serie, :id_deposito, :cant_disponible, :cant_reservado, :cant_preparado, :tipo, :fecha, :observacion)
        """)
        
        # Ejecutar la consulta y obtener el registro insertado directamente
        result = db.execute(query, stock_historico_data)
        row = result.first()
        db.commit()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El registro no se pudo crear"
            )
        
        # Crear un nuevo objeto Stock_historico con los valores devueltos
        new_stock_historico = Stock_historico()
        new_stock_historico.id = row[0]
        new_stock_historico.nro_movimiento = row[1]
        new_stock_historico.codigo_art = row[2]
        new_stock_historico.id_articulos_serie = row[3]
        new_stock_historico.id_deposito = row[4]
        new_stock_historico.cant_disponible = row[5]
        new_stock_historico.cant_reservado = row[6]
        new_stock_historico.cant_preparado = row[7]
        new_stock_historico.tipo = row[8]
        new_stock_historico.fecha = row[9]
        new_stock_historico.observacion = row[10]
        
        return new_stock_historico
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear Stock_historico: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el registro: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear Stock_historico: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )
def get_stock_historico(db: Session, id: int) -> Optional[Stock_historico]:
    """
    Obtiene un registro de Stock_historico por su clave primaria usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, nro_movimiento, codigo_art, id_articulos_serie, id_deposito, cant_disponible, cant_reservado, cant_preparado, tipo, fecha, observacion FROM stock_historico WHERE id = :id"),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock_historico no encontrado.")
        
        # Crear el objeto directamente con los valores
        stock_historico = Stock_historico()
        stock_historico.id = result[0]
        stock_historico.nro_movimiento = result[1]
        stock_historico.codigo_art = result[2]
        stock_historico.id_articulos_serie = result[3]
        stock_historico.id_deposito = result[4]
        stock_historico.cant_disponible = result[5]
        stock_historico.cant_reservado = result[6]
        stock_historico.cant_preparado = result[7]
        stock_historico.tipo = result[8]
        stock_historico.fecha = result[9]
        stock_historico.observacion = result[10]
        
        return stock_historico
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener Stock_historico: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {str(e)}")
def gets_stock_historico(db: Session) -> List[Stock_historico]:
    """
    Obtiene una lista de todos los registros de Stock_historico usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT id, nro_movimiento, codigo_art, id_articulos_serie, id_deposito, cant_disponible, cant_reservado, cant_preparado, tipo, fecha, observacion FROM stock_historico")
        )
        
        stock_historicos = []
        for row in result.fetchall():
            stock_historico = Stock_historico()
            stock_historico.id = row[0]
            stock_historico.nro_movimiento = row[1]
            stock_historico.codigo_art = row[2]
            stock_historico.id_articulos_serie = row[3]
            stock_historico.id_deposito = row[4]
            stock_historico.cant_disponible = row[5]
            stock_historico.cant_reservado = row[6]
            stock_historico.cant_preparado = row[7]
            stock_historico.tipo = row[8]
            stock_historico.fecha = row[9]
            stock_historico.observacion = row[10]
            stock_historicos.append(stock_historico)
        
        return stock_historicos
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de Stock_historico: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {str(e)}")
def delete_stock_historico(db: Session, id: int) -> Stock_historico:
    """
    Elimina un registro de Stock_historico por su clave primaria usando SQL directo.
    """
    try:
        # Obtener y eliminar el registro en una sola operación usando OUTPUT
        result = db.execute(
            text("""
                DELETE FROM stock_historico 
                OUTPUT DELETED.id, DELETED.nro_movimiento, DELETED.codigo_art, DELETED.id_articulos_serie, DELETED.id_deposito, DELETED.cant_disponible, DELETED.cant_reservado, DELETED.cant_preparado, DELETED.tipo, DELETED.fecha, DELETED.observacion
                WHERE id = :id
            """),
            {"id": id}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock_historico no encontrado.")
        
        # Crear el objeto con los datos del registro eliminado
        deleted_stock_historico = Stock_historico()
        deleted_stock_historico.id = result[0]
        deleted_stock_historico.nro_movimiento = result[1]
        deleted_stock_historico.codigo_art = result[2]
        deleted_stock_historico.id_articulos_serie = result[3]
        deleted_stock_historico.id_deposito = result[4]
        deleted_stock_historico.cant_disponible = result[5]
        deleted_stock_historico.cant_reservado = result[6]
        deleted_stock_historico.cant_preparado = result[7]
        deleted_stock_historico.tipo = result[8]
        deleted_stock_historico.fecha = result[9]
        deleted_stock_historico.observacion = result[10]
        
        db.commit()
        return deleted_stock_historico
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar Stock_historico: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {str(e)}")
def update_stock_historico(db: Session, id: int, stock_historico_data: Dict[str, Any]) -> Stock_historico:
    """
    Actualiza un registro de Stock_historico por su clave primaria usando SQL directo.
    """
    logger.info(f"Actualizando Stock_historico con id = {id}")
    try:
        # Verificar que el registro existe
        result = db.execute(
            text("SELECT COUNT(*) FROM stock_historico WHERE id = :id"),
            {"id": id}
        ).scalar()
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock_historico no encontrado.")
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        stock_historico_data_copy = stock_historico_data.copy()
        if 'id' in stock_historico_data_copy:
            del stock_historico_data_copy['id']
        
        # Si no hay campos para actualizar, obtener el registro actual
        if not stock_historico_data_copy:
            return get_stock_historico(db, id)
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in stock_historico_data_copy:
            set_clauses.append(f"{field} = :{field}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa con OUTPUT
        query = text(f"""
            UPDATE stock_historico
            SET {set_clause_str}
            OUTPUT INSERTED.id, INSERTED.nro_movimiento, INSERTED.codigo_art, INSERTED.id_articulos_serie, INSERTED.id_deposito, INSERTED.cant_disponible, INSERTED.cant_reservado, INSERTED.cant_preparado, INSERTED.tipo, INSERTED.fecha, INSERTED.observacion
            WHERE id = :id
        """)
        
        # Preparar los parámetros
        params = stock_historico_data_copy.copy()
        params['id'] = id
        
        # Ejecutar la consulta
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar el Stock_historico.")
        
        # Crear el objeto con los datos actualizados
        updated_stock_historico = Stock_historico()
        updated_stock_historico.id = result[0]
        updated_stock_historico.nro_movimiento = result[1]
        updated_stock_historico.codigo_art = result[2]
        updated_stock_historico.id_articulos_serie = result[3]
        updated_stock_historico.id_deposito = result[4]
        updated_stock_historico.cant_disponible = result[5]
        updated_stock_historico.cant_reservado = result[6]
        updated_stock_historico.cant_preparado = result[7]
        updated_stock_historico.tipo = result[8]
        updated_stock_historico.fecha = result[9]
        updated_stock_historico.observacion = result[10]
        
        return updated_stock_historico
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar Stock_historico: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {str(e)}")
