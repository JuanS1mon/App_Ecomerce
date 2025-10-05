# ============================================================================
# ROUTE CONFIG - BIBLIOTECA_SISTEMA
# ============================================================================
"""
Configurador de rutas para el servicio: biblioteca_sistema
Sistema completo de gestión de biblioteca con autores, libros y préstamos

Este archivo centraliza la configuración de todas las rutas del servicio.
"""

# Imports de terceros
from fastapi import FastAPI

# Imports del proyecto
from sql_app.Services.biblioteca_sistema.autores.route_autores import router as autores_router
from sql_app.Services.biblioteca_sistema.libros.route_libros import router as libros_router

def configure_biblioteca_sistema_routes(app: FastAPI):
    """
    Configura todas las rutas relacionadas con el módulo de biblioteca_sistema
    
    Args:
        app: Instancia de FastAPI donde se registrarán las rutas
    """
    
    # Incluir todos los routers del servicio
    app.include_router(autores_router, prefix="/biblioteca_sistema")
    app.include_router(libros_router, prefix="/biblioteca_sistema")
    
    return app
