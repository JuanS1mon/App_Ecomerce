# ============================================================================
# ROUTE CONFIG - MI_SISTEMA
# ============================================================================
"""
Configurador de rutas para el servicio: mi_sistema
Descripción de mi sistema

Este archivo centraliza la configuración de todas las rutas del servicio.
"""

# Imports de terceros
from fastapi import FastAPI

# Imports del proyecto
from sql_app.Services.mi_sistema.tabla1.route_tabla1 import router as tabla1_router

def configure_mi_sistema_routes(app: FastAPI):
    """
    Configura todas las rutas relacionadas con el módulo de mi_sistema
    
    Args:
        app: Instancia de FastAPI donde se registrarán las rutas
    """
    
    # Incluir todos los routers del servicio
    app.include_router(tabla1_router, prefix="/mi_sistema")
    
    return app
