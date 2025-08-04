# Archivo __init__.py para el servicio facturacion
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from sql_app.Services.app_stock.articulos.model_facturacion import Facturacion
from sql_app.Services.app_stock.articulos.schema_facturacion import FacturacionCreate, FacturacionUpdate, FacturacionRead
from sql_app.Services.app_stock.articulos.service_facturacion import (
    create_facturacion, 
    get_facturacion, 
    gets_facturacion,
    update_facturacion,
    delete_facturacion
)
from sql_app.Services.app_stock.articulos.route_facturacion import router

# Para facilitar la inclusión del router en la aplicación principal
facturacion_router = router

__all__ = [
    'Facturacion',
    'FacturacionCreate',
    'FacturacionUpdate', 
    'FacturacionRead',
    'create_facturacion',
    'get_facturacion',
    'gets_facturacion',
    'update_facturacion',
    'delete_facturacion',
    'router',
    'facturacion_router'
]
