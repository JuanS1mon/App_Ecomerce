# ============================================================================
# ROUTE CONFIG - DM3
# ============================================================================
"""
Configurador de rutas para el servicio: dm3
Sistema multi-tabla generado desde Editor Visual

Este archivo centraliza la configuración de todas las rutas del servicio.
"""

# Imports de terceros
from fastapi import FastAPI

# Imports del proyecto
from sql_app.Services.dm3.usuario_2650.route_usuario_2650 import router as usuario_2650_router
from sql_app.Services.dm3.producto_2650.route_producto_2650 import router as producto_2650_router
from sql_app.Services.dm3.orden_2650.route_orden_2650 import router as orden_2650_router
from sql_app.Services.dm3.detalle_orden_2650.route_detalle_orden_2650 import router as detalle_orden_2650_router
from sql_app.Services.dm3.categoria_2650.route_categoria_2650 import router as categoria_2650_router

def configure_dm3_routes(app: FastAPI):
    """
    Configura todas las rutas relacionadas con el módulo de dm3
    
    Args:
        app: Instancia de FastAPI donde se registrarán las rutas
    """
    
    # Incluir todos los routers del servicio
    app.include_router(usuario_2650_router, prefix="/dm3")
    app.include_router(producto_2650_router, prefix="/dm3")
    app.include_router(orden_2650_router, prefix="/dm3")
    app.include_router(detalle_orden_2650_router, prefix="/dm3")
    app.include_router(categoria_2650_router, prefix="/dm3")
    
    return app
