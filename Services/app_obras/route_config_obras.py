# Imports de terceros
from fastapi import FastAPI

# Imports del proyecto
from sql_app.Services.app_obras.dashboard.route_dashboard import router as dashboard_router, main_router as dashboard_main_router
from sql_app.Services.app_obras.artists.route_artists import router as artists_router
from sql_app.Services.app_obras.artworks.route_artworks import router as artworks_router
from sql_app.Services.app_obras.artwork_states.route_artwork_states import router as artwork_states_router
from sql_app.Services.app_obras.locations.route_locations import router as locations_router
from sql_app.Services.app_obras.institutions.route_institutions import router as institutions_router
from sql_app.Services.app_obras.exhibitions.route_exhibitions import router as exhibitions_router
from sql_app.Services.app_obras.sales.route_sales import router as sales_router
from sql_app.Services.app_obras.documents.route_documents import router as documents_router

# Función para configurar todas las rutas relacionadas con obras
def configure_obras_routes(app: FastAPI):
    """
    Configura todas las rutas relacionadas con el módulo de obras
    
    Args:
        app: Instancia de FastAPI donde se registrarán las rutas
    """
    # Incluir dashboard principal y ruta de acceso principal
    app.include_router(dashboard_router, prefix="/app_obras")
    app.include_router(dashboard_main_router, prefix="/app_obras")
    
    # Incluir los routers principales del sistema de obras de arte
    app.include_router(artists_router, prefix="/app_obras")
    app.include_router(artworks_router, prefix="/app_obras")
    
    # Incluir routers de configuración básica
    app.include_router(artwork_states_router, prefix="/app_obras")
    app.include_router(locations_router, prefix="/app_obras")
    app.include_router(institutions_router, prefix="/app_obras")
    
    # Incluir routers de funcionalidad avanzada
    app.include_router(exhibitions_router, prefix="/app_obras")
    app.include_router(sales_router, prefix="/app_obras")
    app.include_router(documents_router, prefix="/app_obras")
    
    return app