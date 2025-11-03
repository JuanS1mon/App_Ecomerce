"""
Routers del proyecto ecomerce
"""

from .usuarios import router as usuarios_router
from .categorias import router as categorias_router
from .productos import router as productos_router
from .stock import router as stock_router
from .carritos import router as carritos_router
from .carrito_items import router as carrito_items_router
from .pedidos import router as pedidos_router
from .presupuesto import router as presupuesto_router

__all__ = [
    "usuarios_router",
    "categorias_router",
    "productos_router",
    "stock_router",
    "carritos_router",
    "carrito_items_router",
    "pedidos_router",
    "presupuesto_router"
]