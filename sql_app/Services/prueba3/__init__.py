# Archivo __init__.py para el servicio prueba3
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from .model_prueba3 import Prueba3
from .schema_prueba3 import Prueba3Create, Prueba3Update, Prueba3Read
from .service_prueba3 import (
    create_prueba3, 
    get_prueba3, 
    gets_prueba3,
    update_prueba3,
    delete_prueba3
)
from .route_prueba3 import router

# Para facilitar la inclusión del router en la aplicación principal
prueba3_router = router

__all__ = [
    'Prueba3',
    'Prueba3Create',
    'Prueba3Update', 
    'Prueba3Read',
    'create_prueba3',
    'get_prueba3',
    'gets_prueba3',
    'update_prueba3',
    'delete_prueba3',
    'router',
    'prueba3_router'
]
