# Archivo __init__.py para el servicio depositos_tipos
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from sql_app.Services.app_stock.depositos_tipos.model_depositos_tipos import Depositos_tipos
from sql_app.Services.app_stock.depositos_tipos.schema_depositos_tipos import Depositos_tiposCreate, Depositos_tiposUpdate, Depositos_tiposRead
from sql_app.Services.app_stock.depositos_tipos.service_depositos_tipos import (
    create_depositos_tipos, 
    get_depositos_tipos, 
    gets_depositos_tipos,
    update_depositos_tipos,
    delete_depositos_tipos
)
from sql_app.Services.app_stock.depositos_tipos.route_depositos_tipos import router

# Para facilitar la inclusión del router en la aplicación principal
depositos_tipos_router = router

__all__ = [
    'Depositos_tipos',
    'Depositos_tiposCreate',
    'Depositos_tiposUpdate', 
    'Depositos_tiposRead',
    'create_depositos_tipos',
    'get_depositos_tipos',
    'gets_depositos_tipos',
    'update_depositos_tipos',
    'delete_depositos_tipos',
    'router',
    'depositos_tipos_router'
]
