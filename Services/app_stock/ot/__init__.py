# Archivo __init__.py para el servicio ot
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from .model_ot import Ot
from .schema_ot import OtCreate, OtUpdate, OtRead
from .service_ot import (
    create_ot, 
    get_ot, 
    gets_ot,
    update_ot,
    delete_ot
)
from .route_ot import router

# Para facilitar la inclusión del router en la aplicación principal
ot_router = router

__all__ = [
    'Ot',
    'OtCreate',
    'OtUpdate', 
    'OtRead',
    'create_ot',
    'get_ot',
    'gets_ot',
    'update_ot',
    'delete_ot',
    'router',
    'ot_router'
]
