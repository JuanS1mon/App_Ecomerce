# Archivo __init__.py para el servicio articulos
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from .model_articulos import Articulos
from .schema_articulos import ArticulosCreate, ArticulosUpdate, ArticulosRead
from .service_articulos import (
    create_articulos, 
    get_articulos, 
    gets_articulos,
    update_articulos,
    delete_articulos
)
from .route_articulos import router

# Para facilitar la inclusión del router en la aplicación principal
articulos_router = router

__all__ = [
    'Articulos',
    'ArticulosCreate',
    'ArticulosUpdate', 
    'ArticulosRead',
    'create_articulos',
    'get_articulos',
    'gets_articulos',
    'update_articulos',
    'delete_articulos',
    'router',
    'articulos_router'
]
