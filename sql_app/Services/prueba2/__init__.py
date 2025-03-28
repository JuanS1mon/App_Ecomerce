# Archivo __init__.py para el servicio prueba2
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from .model_prueba2 import Prueba2
from .schema_prueba2 import Prueba2Create, Prueba2Update, Prueba2Read
from .service_prueba2 import (
    create_prueba2, 
    get_prueba2, 
    gets_prueba2,
    update_prueba2,
    delete_prueba2
)
from .route_prueba2 import router

# Para facilitar la inclusión del router en la aplicación principal
prueba2_router = router

__all__ = [
    'Prueba2',
    'Prueba2Create',
    'Prueba2Update', 
    'Prueba2Read',
    'create_prueba2',
    'get_prueba2',
    'gets_prueba2',
    'update_prueba2',
    'delete_prueba2',
    'router',
    'prueba2_router'
]
