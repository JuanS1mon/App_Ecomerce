# Archivo __init__.py para el servicio stock_historico
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from Services.app_stock.stock_historico.model_stock_historico import Stock_historico
from Services.app_stock.stock_historico.schema_stock_historico import Stock_historicoCreate, Stock_historicoUpdate, Stock_historicoRead
from Services.app_stock.stock_historico.service_stock_historico import (
    create_stock_historico, 
    get_stock_historico, 
    gets_stock_historico,    update_stock_historico,
    delete_stock_historico
)
from Services.app_stock.stock_historico.route_stock_historico import router

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
