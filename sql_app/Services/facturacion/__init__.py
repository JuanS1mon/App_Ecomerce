# Archivo __init__.py para el servicio facturacion
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from .model_facturacion import Facturacion
from .schema_facturacion import FacturacionCreate, FacturacionUpdate, FacturacionRead
from .service_facturacion import (
    create_facturacion, 
    get_facturacion, 
    gets_facturacion,
    update_facturacion,
    delete_facturacion
)
from .route_facturacion import router

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
