# Archivo __init__.py para el servicio depositos
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from sql_app.Services.app_stock.depositos.model_depositos import Depositos
from sql_app.Services.app_stock.depositos.schema_depositos import DepositosCreate, DepositosUpdate, DepositosRead
from sql_app.Services.app_stock.depositos.service_depositos import (
    create_depositos, 
    get_depositos, 
    gets_depositos,
    update_depositos,
    delete_depositos
)
from sql_app.Services.app_stock.depositos.route_depositos import router

# Para facilitar la inclusión del router en la aplicación principal
depositos_router = router

__all__ = [
    'Depositos',
    'DepositosCreate',
    'DepositosUpdate', 
    'DepositosRead',
    'create_depositos',
    'get_depositos',
    'gets_depositos',
    'update_depositos',
    'delete_depositos',
    'router',
    'depositos_router'
]
