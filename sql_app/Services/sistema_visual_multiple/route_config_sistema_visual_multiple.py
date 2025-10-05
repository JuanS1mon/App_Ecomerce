# ============================================================================
# ROUTE CONFIG - SISTEMA_VISUAL_MULTIPLE
# ============================================================================
"""
Configurador de rutas para el servicio: sistema_visual_multiple
Sistema multi-tabla generado desde Editor Visual

Este archivo centraliza la configuración de todas las rutas del servicio.
"""

# Imports de terceros
from fastapi import FastAPI

# Imports del proyecto
from sql_app.Services.sistema_visual_multiple.usuario_5862.route_usuario_5862 import router as usuario_5862_router
from sql_app.Services.sistema_visual_multiple.producto_5862.route_producto_5862 import router as producto_5862_router
from sql_app.Services.sistema_visual_multiple.orden_5862.route_orden_5862 import router as orden_5862_router
from sql_app.Services.sistema_visual_multiple.detalle_orden_5862.route_detalle_orden_5862 import router as detalle_orden_5862_router
from sql_app.Services.sistema_visual_multiple.categoria_5862.route_categoria_5862 import router as categoria_5862_router

def configure_sistema_visual_multiple_routes(app: FastAPI):
    """
    Configura todas las rutas relacionadas con el módulo de sistema_visual_multiple
    
    Args:
        app: Instancia de FastAPI donde se registrarán las rutas
    """
    
    # Incluir todos los routers del servicio
    app.include_router(usuario_5862_router, prefix="/sistema_visual_multiple")
    app.include_router(producto_5862_router, prefix="/sistema_visual_multiple")
    app.include_router(orden_5862_router, prefix="/sistema_visual_multiple")
    app.include_router(detalle_orden_5862_router, prefix="/sistema_visual_multiple")
    app.include_router(categoria_5862_router, prefix="/sistema_visual_multiple")
    
    return app
