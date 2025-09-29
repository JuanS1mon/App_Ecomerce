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
from sql_app.Services.sistema_visual_multiple.usuario_7306.route_usuario_7306 import router as usuario_7306_router
from sql_app.Services.sistema_visual_multiple.producto_7306.route_producto_7306 import router as producto_7306_router
from sql_app.Services.sistema_visual_multiple.orden_7306.route_orden_7306 import router as orden_7306_router
from sql_app.Services.sistema_visual_multiple.detalle_orden_7306.route_detalle_orden_7306 import router as detalle_orden_7306_router
from sql_app.Services.sistema_visual_multiple.categoria_7306.route_categoria_7306 import router as categoria_7306_router

def configure_sistema_visual_multiple_routes(app: FastAPI):
    """
    Configura todas las rutas relacionadas con el módulo de sistema_visual_multiple
    
    Args:
        app: Instancia de FastAPI donde se registrarán las rutas
    """
    
    # Incluir todos los routers del servicio
    app.include_router(usuario_7306_router, prefix="/sistema_visual_multiple")
    app.include_router(producto_7306_router, prefix="/sistema_visual_multiple")
    app.include_router(orden_7306_router, prefix="/sistema_visual_multiple")
    app.include_router(detalle_orden_7306_router, prefix="/sistema_visual_multiple")
    app.include_router(categoria_7306_router, prefix="/sistema_visual_multiple")
    
    return app
