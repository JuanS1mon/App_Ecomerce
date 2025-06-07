# Archivo __init__.py para el servicio articulos
# Este archivo permite importar componentes del servicio desde otras partes de la aplicación

from .model_articulos import Articulos
from .model_precios_historial import PreciosHistorial
from .schema_articulos import (
    ArticulosCreate, 
    ArticulosUpdate, 
    ArticulosRead,
    CodigoBarrasRequest,
    QRCodeRequest
)
from .schema_precios_historial import (
    PreciosHistorialRead, 
    PreciosHistorialCreate, 
    PreciosHistorialUpdate
)
from .service_articulos import (
    create_articulos, 
    get_articulos, 
    gets_articulos,
    update_articulos,
    delete_articulos,
    actualizar_precio_articulo,
    actualizar_precios_masivos
)
from .service_precios_historial import (
    registrar_cambio_precio,
    obtener_historial_por_articulo,
    busqueda_avanzada_historial
)
from .service_codigos import (
    generar_codigo_barras,
    generar_codigo_qr,
    generar_etiqueta_completa
)
from .route_articulos import router as articulos_router
from .route_historial_precios import router as historial_router
# Importación ficticia para mantener la estructura correcta, se implementará más tarde
from .route_articulos import router as codigos_router  # Placeholder hasta que se implemente el router de códigos

# Para facilitar la inclusión del router en la aplicación principal
router = [
    articulos_router,
    historial_router,
    codigos_router
]

__all__ = [
    # Modelos
    'Articulos',
    'PreciosHistorial',
    
    # Esquemas
    'ArticulosCreate',
    'ArticulosUpdate', 
    'ArticulosRead',
    'CodigoBarrasRequest',
    'QRCodeRequest',
    'PreciosHistorialRead', 
    'PreciosHistorialCreate', 
    'PreciosHistorialUpdate',
    
    # Servicios de artículos
    'create_articulos',
    'get_articulos',
    'gets_articulos',
    'update_articulos',
    'delete_articulos',
    'actualizar_precio_articulo',
    'actualizar_precios_masivos',
    
    # Servicios de historial de precios
    'registrar_cambio_precio',
    'obtener_historial_por_articulo',
    'busqueda_avanzada_historial',
    
    # Servicios de códigos
    'generar_codigo_barras',
    'generar_codigo_qr',
    'generar_etiqueta_completa',
    
    # Routers
    'articulos_router',
    'historial_router',
    'codigos_router',
    'router'
]
