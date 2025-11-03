"""
Proyecto ecomerce - Generado desde Editor Visual
Archivo principal de inicialización del proyecto.
"""

# Importaciones de modelos (con prefijo)
from .models.usuarios import EcomerceUsuarios
from .schemas.usuarios import UsuariosCreate, UsuariosUpdate, UsuariosRead
from .Controllers.usuarios import create_usuarios, get_usuarios, gets_usuarios, update_usuarios, delete_usuarios
from .models.categorias import EcomerceCategorias
from .schemas.categorias import CategoriasCreate, CategoriasUpdate, CategoriasRead
from .Controllers.categorias import create_categorias, get_categorias, gets_categorias, update_categorias, delete_categorias
from .models.productos import EcomerceProductos
from .schemas.productos import ProductosCreate, ProductosUpdate, ProductosRead
from .Controllers.productos import create_productos, get_productos, gets_productos, update_productos, delete_productos
from .models.stock import EcomerceStock
from .schemas.stock import StockCreate, StockUpdate, StockRead
from .Controllers.stock import create_stock, get_stock, gets_stock, update_stock, delete_stock
from .models.carritos import EcomerceCarritos
from .schemas.carritos import CarritosCreate, CarritosUpdate, CarritosRead
from .Controllers.carritos import create_carritos, get_carritos, gets_carritos, update_carritos, delete_carritos
from .models.carrito_items import EcomerceCarrito_items
from .schemas.carrito_items import Carrito_itemsCreate, Carrito_itemsUpdate, Carrito_itemsRead
from .Controllers.carrito_items import create_carrito_items, get_carrito_items, gets_carrito_items, update_carrito_items, delete_carrito_items
from .models.pedidos import EcomercePedidos
from .schemas.pedidos import PedidosCreate, PedidosUpdate, PedidosRead
from .Controllers.pedidos import create_pedidos, get_pedidos, gets_pedidos, update_pedidos, delete_pedidos

# Importaciones de rutas
from .routes.usuarios import router as usuarios_router
from .routes.categorias import router as categorias_router
from .routes.productos import router as productos_router
from .routes.stock import router as stock_router
from .routes.carritos import router as carritos_router
from .routes.carrito_items import router as carrito_items_router
from .routes.pedidos import router as pedidos_router
from .routes.presupuesto import router as presupuesto_router

# Lista de todos los componentes disponibles
__all__ = [
    # Modelos
    "EcomerceUsuarios", "EcomerceCategorias", "EcomerceProductos", "EcomerceStock", "EcomerceCarritos", "EcomerceCarrito_items", "EcomercePedidos",
    # Schemas
    "UsuariosCreate", "UsuariosUpdate", "UsuariosRead", "CategoriasCreate", "CategoriasUpdate", "CategoriasRead", "ProductosCreate", "ProductosUpdate", "ProductosRead", "StockCreate", "StockUpdate", "StockRead", "CarritosCreate", "CarritosUpdate", "CarritosRead", "Carrito_itemsCreate", "Carrito_itemsUpdate", "Carrito_itemsRead", "PedidosCreate", "PedidosUpdate", "PedidosRead",
    # Controladores
    "create_usuarios", "get_usuarios", "gets_usuarios", "update_usuarios", "delete_usuarios", "create_categorias", "get_categorias", "gets_categorias", "update_categorias", "delete_categorias", "create_productos", "get_productos", "gets_productos", "update_productos", "delete_productos", "create_stock", "get_stock", "gets_stock", "update_stock", "delete_stock", "create_carritos", "get_carritos", "gets_carritos", "update_carritos", "delete_carritos", "create_carrito_items", "get_carrito_items", "gets_carrito_items", "update_carrito_items", "delete_carrito_items", "create_pedidos", "get_pedidos", "gets_pedidos", "update_pedidos", "delete_pedidos",
    # Rutas
    "usuarios_router", "categorias_router", "productos_router", "stock_router", "carritos_router", "carrito_items_router", "pedidos_router", "presupuesto_router",
]
