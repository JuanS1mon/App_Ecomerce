# Archivo __init__.py para el servicio stock_historico
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from sql_app.Services.app_stock.articulos.model_stock_historico import Stock_historico
from sql_app.Services.app_stock.articulos.schema_stock_historico import Stock_historicoCreate, Stock_historicoUpdate, Stock_historicoRead
from sql_app.Services.app_stock.articulos.service_stock_historico import (
    create_stock_historico, 
    get_stock_historico, 
    gets_stock_historico,
    update_stock_historico,
    delete_stock_historico
)
from sql_app.Services.app_stock.articulos.route_stock_historico import router

# Para facilitar la inclusión del router en la aplicación principal
stock_historico_router = router

__all__ = [
    'Stock_historico',
    'Stock_historicoCreate',
    'Stock_historicoUpdate', 
    'Stock_historicoRead',
    'create_stock_historico',
    'get_stock_historico',
    'gets_stock_historico',
    'update_stock_historico',
    'delete_stock_historico',
    'router',
    'stock_historico_router'
]
