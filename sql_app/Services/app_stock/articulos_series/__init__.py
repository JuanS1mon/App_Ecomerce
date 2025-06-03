# Archivo __init__.py para el servicio articulos_series
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from .model_articulos_series import Articulos_series
from .schema_articulos_series import Articulos_seriesCreate, Articulos_seriesUpdate, Articulos_seriesRead
from .service_articulos_series import (
    create_articulos_series, 
    get_articulos_series, 
    gets_articulos_series,
    update_articulos_series,
    delete_articulos_series
)
from .route_articulos_series import router

# Para facilitar la inclusión del router en la aplicación principal
articulos_series_router = router

__all__ = [
    'Articulos_series',
    'Articulos_seriesCreate',
    'Articulos_seriesUpdate', 
    'Articulos_seriesRead',
    'create_articulos_series',
    'get_articulos_series',
    'gets_articulos_series',
    'update_articulos_series',
    'delete_articulos_series',
    'router',
    'articulos_series_router'
]
