# Archivo __init__.py para el servicio articulos_tipos
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from .model_articulos_tipos import Articulos_tipos
from .schema_articulos_tipos import Articulos_tiposCreate, Articulos_tiposUpdate, Articulos_tiposRead
from .service_articulos_tipos import (
    create_articulos_tipos, 
    get_articulos_tipos, 
    gets_articulos_tipos,
    update_articulos_tipos,
    delete_articulos_tipos
)
from .route_articulos_tipos import router

# Para facilitar la inclusión del router en la aplicación principal
articulos_tipos_router = router

__all__ = [
    'Articulos_tipos',
    'Articulos_tiposCreate',
    'Articulos_tiposUpdate', 
    'Articulos_tiposRead',
    'create_articulos_tipos',
    'get_articulos_tipos',
    'gets_articulos_tipos',
    'update_articulos_tipos',
    'delete_articulos_tipos',
    'router',
    'articulos_tipos_router'
]
