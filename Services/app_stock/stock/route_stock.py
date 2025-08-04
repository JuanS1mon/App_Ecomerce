import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from sql_app.db.database import get_db
from sql_app.Services.app_stock.articulos.model_articulos import Articulos as ArticulosModel
from sql_app.Services.app_stock.articulos.schema_articulos import ArticulosRead
from sql_app.Services.app_stock.stock.model_stock import Stock as StockModel
from sql_app.Services.app_stock.stock.schema_stock import StockCreate, StockRead, StockUpdate
from sql_app.Services.app_stock.stock.service_stock import (
    anular_movimiento,
    create_stock,
    delete_stock,
    get_stock,
    gets_stock,
    update_stock
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/stock",
    tags=["stock"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.put("/anular/{nro_movimiento}")
def anular_movimiento_route(nro_movimiento: int, db: Session = Depends(get_db)):
    cantidad = anular_movimiento(db, nro_movimiento)
    if cantidad == 0:
        raise HTTPException(status_code=404, detail="No se encontraron registros con ese movimiento")
    return {"mensaje": f"Movimiento {nro_movimiento} anulado correctamente ({cantidad} registros)"}

@router.post("/", response_model=List[StockRead])
async def routes_post_stock(stock: StockCreate, db: Session = Depends(get_db)):
    logger.info("Creando nuevo movimiento de stock")

    try:
        stock_data = stock.model_dump()
        id_destino = stock_data.pop("id_deposito_destino")

        # Obtener el último nro_movimiento de la base y sumarle 1
        ultimo_mov = db.execute(text("SELECT ISNULL(MAX(nro_movimiento), 0) FROM stock")).scalar()
        nuevo_nro_movimiento = ultimo_mov + 1
        stock_data["nro_movimiento"] = nuevo_nro_movimiento


        # Consulta para obtener el stock actual del depósito origen
        actual_origen = db.execute(text("""
            SELECT TOP 1 cant_disponible, cant_reservado FROM stock 
            WHERE id_deposito = :id_dep ORDER BY id DESC
        """), {"id_dep": stock_data["id_deposito"]}).fetchone() or (0, 0)

        cant_disponible = actual_origen[0] - stock_data["cant_reservado"]
        cant_reservado = stock_data["cant_reservado"]



        stock_origen = StockModel(**stock_data)
        stock_origen.cant_disponible = cant_disponible
        stock_origen.cant_reservado = cant_reservado
        stock_origen.cant_preparado = 0

        # Consulta para obtener el stock actual del depósito destino
        actual_destino = db.execute(text("""
            SELECT TOP 1 cant_preparado FROM stock 
            WHERE id_deposito = :id_dep ORDER BY id DESC
        """), {"id_dep": id_destino}).fetchone() or (0,)

        stock_destino = StockModel(**stock_data)
        stock_destino.id_deposito = id_destino
        stock_destino.cant_disponible = 0
        stock_destino.cant_reservado = 0
        stock_destino.cant_preparado = stock_data["cant_reservado"]


        resultados = create_stock(db=db, stock_origen=stock_origen, stock_destino=stock_destino)
        return [StockRead.model_validate(x) for x in resultados]

    except Exception as e:
        logger.error(f"Error al crear Stock: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/id/{id}", response_model=StockRead)
async def routes_get_stock_id(id: int, db: Session = Depends(get_db)):
    try:
        db_stock = get_stock(db, id)
        if not db_stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: stock no encontrado")
        return StockRead.model_validate(db_stock)
    except Exception as e:
        logger.error(f"Error al obtener Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[StockRead])
async def routes_gets_stock_all(db: Session = Depends(get_db)):
    try:
        db_stock = gets_stock(db)
        if not db_stock:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: stocks no encontrados")
        return [StockRead.model_validate(stock) for stock in db_stock]
    except Exception as e:
        logger.error(f"Error al obtener registros de Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=StockRead)
async def routes_delete_stock_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_stock = get_stock(db, id)
        if not resultado_stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: stock no encontrado")
        db_stock = delete_stock(db, id)
        return StockRead.model_validate(db_stock)
    except Exception as e:
        logger.error(f"Error al eliminar Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

@router.get("/depositos", response_model=List[Dict[str, Any]])
def get_depositos(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT id, descripcion FROM depositos ORDER BY descripcion")).fetchall()
    return [{"id": row.id, "descripcion": row.descripcion} for row in result]

@router.get("/stock_actual/{id_deposito}")
def get_stock_actual(id_deposito: int, db: Session = Depends(get_db)):
    try:
        result = db.execute(text("""
            SELECT TOP 1 cant_disponible, cant_preparado 
            FROM stock 
            WHERE id_deposito = :id_deposito
            ORDER BY id DESC
        """), {"id_deposito": id_deposito}).fetchone()

        if result:
            return {"cant_disponible": result.cant_disponible, "cant_preparado": result.cant_preparado}
        else:
            return {"cant_disponible": 0, "cant_preparado": 0}

    except Exception as e:
        logger.error(f"Error al obtener stock actual: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener stock actual.")

@router.put("/id/{id}", response_model=StockRead)
async def routes_update_stock(id: int, stock: StockUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Stock con id = {id}")
    try:
        stock_data = stock.model_dump()
        db_stock = update_stock(db=db, id=id, stock_data=stock_data)
        return StockRead.model_validate(db_stock)
    except Exception as e:
        logger.error(f"Error al actualizar Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Ruta actualizada: ahora buscamos en static/module_name/index.html
        with open(f"sql_app/static/stock/stock.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")


@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """
    Endpoint que sirve la página del dashboard de stock
    """
    try:
        # Modificado para usar la función de respuesta directa y no leer el archivo
        return HTMLResponse(content=html_dashboard_content())
    except Exception as e:
        logger.error(f"Error al obtener la página del dashboard: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                          detail="Error al cargar el dashboard de stock.")

def html_dashboard_content():
    """
    Función que devuelve el contenido HTML del dashboard como una cadena de texto
    en lugar de leerlo desde un archivo para evitar problemas de codificación.
    """
    return """"""


@router.get("/api/dashboard-data")
async def get_dashboard_data(db: Session = Depends(get_db)):
    """
    Endpoint API que devuelve los datos necesarios para el dashboard
    """
    try:
        # Obtener todos los registros de stock
        stock_items = gets_stock(db)
        
        # Crear algunos datos "mock" basados en los artículos disponibles
        # Ya que no tenemos todas las columnas en la tabla real
        
        # Ejemplo de datos para el dashboard adaptado a nuestras columnas disponibles
        dashboard_data = {
            "total_items": len(stock_items),
            "total_value": len(stock_items) * 1000,  # Valor ficticio ya que no tenemos precios
            "low_stock_items": [],
            "recent_movements": [StockRead.model_validate(item) for item in stock_items[-10:]] if stock_items else []
        }
        
        # Generar algunos datos de ejemplo para los artículos con stock bajo
        # hasta que la tabla real tenga estos campos
        low_stock_mock = []
        for i, item in enumerate(stock_items[:5]):  # Tomamos los primeros 5 como ejemplo
            low_stock_item = StockRead.model_validate(item)
            # Añadimos propiedades para la interfaz (estos valores no existen en la BD real)
            setattr(low_stock_item, "descripcion", f"Artículo de prueba {i+1}")
            setattr(low_stock_item, "cant_disponible", i + 3)  # Valores simulados entre 3 y 7
            low_stock_mock.append(low_stock_item)
            
        dashboard_data["low_stock_items"] = low_stock_mock
        
        return dashboard_data
    except Exception as e:
        logger.error(f"Error al obtener datos para el dashboard: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                           detail="Error al procesar los datos del dashboard.")
@router.get("/codigo/{codigo}", response_model=ArticulosRead)
async def get_articulo_by_codigo(codigo: str, db: Session = Depends(get_db)):
    try:
        result = db.execute(
            text("SELECT id, codigo, descripcion, preciocosto, precioventa, modelo, marca, id_tipo FROM articulos WHERE codigo = :codigo"),
            {"codigo": codigo}
        ).first()

        if not result:
            raise HTTPException(status_code=404, detail="Artículo no encontrado")

        articulo = ArticulosModel()
        articulo.id = result[0]
        articulo.codigo = result[1]
        articulo.descripcion = result[2]
        articulo.preciocosto = result[3]
        articulo.precioventa = result[4]
        articulo.modelo = result[5]
        articulo.marca = result[6]
        articulo.id_tipo = result[7]

        return ArticulosRead.model_validate(articulo)

    except Exception as e:
        logger.error(f"Error al obtener artículo por código: {e}")
        raise HTTPException(status_code=500, detail="Error al buscar artículo por código")
