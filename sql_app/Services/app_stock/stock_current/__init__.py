# Archivo __init__.py para el servicio stock_current
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from .model_stock_current import Stock_current
from .schema_stock_current import Stock_currentCreate, Stock_currentUpdate, Stock_currentRead
from .service_stock_current import (
    create_stock_current, 
    get_stock_current, 
    gets_stock_current,
    update_stock_current,
    delete_stock_current
)
from .route_stock_current import router

# Para facilitar la inclusión del router en la aplicación principal
stock_current_router = router

__all__ = [
    'Stock_current',
    'Stock_currentCreate',
    'Stock_currentUpdate', 
    'Stock_currentRead',
    'create_stock_current',
    'get_stock_current',
    'gets_stock_current',
    'update_stock_current',
    'delete_stock_current',
    'router',
    'stock_current_router'
]
