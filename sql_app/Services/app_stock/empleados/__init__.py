# Archivo __init__.py para el servicio empleados
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from .model_empleados import Empleados
from .schema_empleados import EmpleadosCreate, EmpleadosUpdate, EmpleadosRead
from .service_empleados import (
    create_empleados, 
    get_empleados, 
    gets_empleados,
    update_empleados,
    delete_empleados
)
from .route_empleados import router

# Para facilitar la inclusión del router en la aplicación principal
empleados_router = router

__all__ = [
    'Empleados',
    'EmpleadosCreate',
    'EmpleadosUpdate', 
    'EmpleadosRead',
    'create_empleados',
    'get_empleados',
    'gets_empleados',
    'update_empleados',
    'delete_empleados',
    'router',
    'empleados_router'
]
