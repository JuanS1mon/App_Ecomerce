# Archivo __init__.py para el servicio test1
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from .model_test1 import Test1
from .schema_test1 import Test1Create, Test1Update, Test1Read
from .service_test1 import (
    create_test1, 
    get_test1, 
    gets_test1,
    update_test1,
    delete_test1
)
from .route_test1 import router as test1_router

# Para facilitar la inclusión del router en la aplicación principal
__all__ = [
    'Test1',
    'Test1Create',
    'Test1Update', 
    'Test1Read',
    'create_test1',
    'get_test1',
    'gets_test1',
    'update_test1',
    'delete_test1',
    'test1_router'
]
