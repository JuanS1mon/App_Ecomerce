"""
Configuración de rutas para el proyecto ecomerce
"""

from fastapi import FastAPI
from . import (
    usuarios_router,
    categorias_router,
    productos_router,
    stock_router,
    carritos_router,
    carrito_items_router,
    pedidos_router,
    presupuesto_router,
    checkout_router,
)


def configure_routes(app: FastAPI):
    """
    Configura todas las rutas del proyecto ecomerce

    Args:
        app: Instancia de FastAPI
    """
    app.include_router(usuarios_router, prefix="/ecomerce/usuarios", tags=["usuarios"])
    app.include_router(categorias_router, prefix="/ecomerce/categorias", tags=["categorias"])
    app.include_router(productos_router, prefix="/ecomerce/productos", tags=["productos"])
    app.include_router(stock_router, prefix="/ecomerce/stock", tags=["stock"])
    app.include_router(carritos_router, prefix="/ecomerce/carritos", tags=["carritos"])
    app.include_router(carrito_items_router, prefix="/ecomerce/carrito_items", tags=["carrito_items"])
    app.include_router(pedidos_router, prefix="/ecomerce/pedidos", tags=["pedidos"])
    app.include_router(presupuesto_router, prefix="/ecomerce/api", tags=["presupuesto"])
    app.include_router(checkout_router, prefix="/ecomerce/checkout", tags=["checkout"])

    return app
