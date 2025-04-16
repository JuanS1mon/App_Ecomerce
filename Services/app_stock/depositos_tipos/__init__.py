# Archivo __init__.py para el servicio depositos_tipos
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from .model_depositos_tipos import Depositos_tipos
from .schema_depositos_tipos import Depositos_tiposCreate, Depositos_tiposUpdate, Depositos_tiposRead
from .service_depositos_tipos import (
    create_depositos_tipos, 
    get_depositos_tipos, 
    gets_depositos_tipos,
    update_depositos_tipos,
    delete_depositos_tipos
)
from .route_depositos_tipos import router

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
