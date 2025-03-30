# Archivo __init__.py para el servicio depositos_tipo
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from .model_depositos_tipo import Depositos_tipo
from .schema_depositos_tipo import Depositos_tipoCreate, Depositos_tipoUpdate, Depositos_tipoRead
from .service_depositos_tipo import (
    create_depositos_tipo, 
    get_depositos_tipo, 
    gets_depositos_tipo,
    update_depositos_tipo,
    delete_depositos_tipo
)
from .route_depositos_tipo import router

# Para facilitar la inclusión del router en la aplicación principal
depositos_tipo_router = router

__all__ = [
    'Depositos_tipo',
    'Depositos_tipoCreate',
    'Depositos_tipoUpdate', 
    'Depositos_tipoRead',
    'create_depositos_tipo',
    'get_depositos_tipo',
    'gets_depositos_tipo',
    'update_depositos_tipo',
    'delete_depositos_tipo',
    'router',
    'depositos_tipo_router'
]
