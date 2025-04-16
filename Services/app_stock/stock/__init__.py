# Archivo __init__.py para el servicio stock
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from .model_stock import Stock
from .schema_stock import StockCreate, StockUpdate, StockRead
from .service_stock import (
    create_stock, 
    get_stock, 
    gets_stock,
    update_stock,
    delete_stock
)
from .route_stock import router

# Para facilitar la inclusión del router en la aplicación principal
stock_router = router

__all__ = [
    'Stock',
    'StockCreate',
    'StockUpdate', 
    'StockRead',
    'create_stock',
    'get_stock',
    'gets_stock',
    'update_stock',
    'delete_stock',
    'router',
    'stock_router'
]
