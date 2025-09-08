# Archivo __init__.py para el servicio clientes
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from .model_clientes import Clientes
from .schema_clientes import ClientesCreate, ClientesUpdate, ClientesRead
from .service_clientes import (
    create_clientes, 
    get_clientes, 
    gets_clientes,
    update_clientes,
    delete_clientes
)
from .route_clientes import router

# Para facilitar la inclusión del router en la aplicación principal
clientes_router = router

__all__ = [
    'Clientes',
    'ClientesCreate',
    'ClientesUpdate', 
    'ClientesRead',
    'create_clientes',
    'get_clientes',
    'gets_clientes',
    'update_clientes',
    'delete_clientes',
    'router',
    'clientes_router'
]
