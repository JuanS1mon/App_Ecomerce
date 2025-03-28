# Archivo __init__.py para el servicio facu_gay
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from .model_facu_gay import Facu_gay
from .schema_facu_gay import Facu_gayCreate, Facu_gayUpdate, Facu_gayRead
from .service_facu_gay import (
    create_facu_gay, 
    get_facu_gay, 
    gets_facu_gay,
    update_facu_gay,
    delete_facu_gay
)
from .route_facu_gay import router

# Para facilitar la inclusión del router en la aplicación principal
facu_gay_router = router

__all__ = [
    'Facu_gay',
    'Facu_gayCreate',
    'Facu_gayUpdate', 
    'Facu_gayRead',
    'create_facu_gay',
    'get_facu_gay',
    'gets_facu_gay',
    'update_facu_gay',
    'delete_facu_gay',
    'router',
    'facu_gay_router'
]
