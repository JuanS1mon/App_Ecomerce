# Archivo __init__.py para el servicio obras
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from .model_obras import Obras
from .schema_obras import ObrasCreate, ObrasUpdate, ObrasRead
from .service_obras import (
    create_obras, 
    get_obras, 
    gets_obras,
    update_obras,
    delete_obras
)
from .route_obras import router

# Para facilitar la inclusión del router en la aplicación principal
obras_router = router

__all__ = [
    'Obras',
    'ObrasCreate',
    'ObrasUpdate', 
    'ObrasRead',
    'create_obras',
    'get_obras',
    'gets_obras',
    'update_obras',
    'delete_obras',
    'router',
    'obras_router'
]
