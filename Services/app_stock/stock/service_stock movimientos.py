# Imports de bibliotecas estándar
from sql_app.Services.app_stock.stock.model_stock import Stock  # Corregida la importación
from sql_app.Services.app_stock.stock.model_stock import Stock as StockModel
from typing import List, Optional, Dict, Any
import logging

# Imports de terceros
from fastapi import HTTPException, status
from sqlalchemy import text,func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def create_stock(db: Session, stock: StockModel, deposito_destino: int):
    # Buscar último nro_movimiento
    max_nro = db.query(func.max(StockModel.nro_movimiento)).scalar() or 0
    nro = max_nro + 1

    # Buscar último stock del depósito emisor
    stock_anterior = (
        db.query(StockModel)
        .filter(StockModel.id_deposito == stock.id_deposito)
        .order_by(StockModel.id.desc())
        .first()
    )
    cant_disp = (stock_anterior.cant_disponible if stock_anterior else 0) - stock.cant_reservado
    cant_res = (stock_anterior.cant_reservado if stock_anterior else 0) + stock.cant_reservado

    # Insertar movimiento de egreso (dep. emisor)
    salida = StockModel(
        nro_movimiento=nro,
        codigo_art=stock.codigo_art,
        id_articulos_serie=stock.id_articulos_serie,
        id_deposito=stock.id_deposito,
        cant_disponible=cant_disp,
        cant_reservado=cant_res,
        cant_preparado=stock.cant_preparado,
        tipo=stock.tipo,
        fecha=stock.fecha,
        observacion=stock.observacion
    )
    db.add(salida)

    # Buscar último stock del depósito receptor
    stock_destino = (
        db.query(StockModel)
        .filter(StockModel.id_deposito == deposito_destino)
        .order_by(StockModel.id.desc())
        .first()
    )
    cant_disp_dest = stock_destino.cant_disponible if stock_destino else 0
    cant_res_dest = stock_destino.cant_reservado if stock_destino else 0
    cant_prep_dest = (stock_destino.cant_preparado if stock_destino else 0) + stock.cant_reservado

    # Insertar movimiento de ingreso (dep. receptor)
    ingreso = StockModel(
        nro_movimiento=nro,
        codigo_art=stock.codigo_art,
        id_articulos_serie=stock.id_articulos_serie,
        id_deposito=deposito_destino,
        cant_disponible=cant_disp_dest,
        cant_reservado=cant_res_dest,
        cant_preparado=cant_prep_dest,
        tipo=stock.tipo,
        fecha=stock.fecha,
        observacion=stock.observacion
    )
    db.add(ingreso)

    db.commit()
    db.refresh(salida)  # Podés devolver el movimiento de salida si querés

    return salida



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
