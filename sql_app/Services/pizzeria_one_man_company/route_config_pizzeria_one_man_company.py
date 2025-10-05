# ============================================================================
# ROUTE CONFIG - PIZZERIA_ONE_MAN_COMPANY
# ============================================================================
"""
Configurador de rutas para el servicio: pizzeria_one_man_company
Aplicación para una pizzería operada por una sola persona, con tablas para gestionar productos, ingredientes, recetas y pedidos. Diseñada para que agentes de AI automaticen ventas, compras y optimización de rentabilidad.

Este archivo centraliza la configuración de todas las rutas del servicio.
"""

# Imports de terceros
from fastapi import FastAPI

# Imports del proyecto
from sql_app.Services.pizzeria_one_man_company.usuarios.route_usuarios import router as usuarios_router
from sql_app.Services.pizzeria_one_man_company.clientes.route_clientes import router as clientes_router
from sql_app.Services.pizzeria_one_man_company.productos.route_productos import router as productos_router
from sql_app.Services.pizzeria_one_man_company.ingredientes.route_ingredientes import router as ingredientes_router
from sql_app.Services.pizzeria_one_man_company.recetas.route_recetas import router as recetas_router
from sql_app.Services.pizzeria_one_man_company.pedidos.route_pedidos import router as pedidos_router

def configure_pizzeria_one_man_company_routes(app: FastAPI):
    """
    Configura todas las rutas relacionadas con el módulo de pizzeria_one_man_company
    
    Args:
        app: Instancia de FastAPI donde se registrarán las rutas
    """
    
    # Incluir todos los routers del servicio
    app.include_router(usuarios_router, prefix="/pizzeria_one_man_company")
    app.include_router(clientes_router, prefix="/pizzeria_one_man_company")
    app.include_router(productos_router, prefix="/pizzeria_one_man_company")
    app.include_router(ingredientes_router, prefix="/pizzeria_one_man_company")
    app.include_router(recetas_router, prefix="/pizzeria_one_man_company")
    app.include_router(pedidos_router, prefix="/pizzeria_one_man_company")
    
    return app
