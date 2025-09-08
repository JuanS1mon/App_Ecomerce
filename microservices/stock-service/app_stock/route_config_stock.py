# Imports de terceros
from fastapi import FastAPI

# Imports del proyecto
from sql_app.Services.app_stock.ot.route_ot import router as ot_router
from sql_app.Services.app_stock.articulos.route_articulos import router as articulos_router
from sql_app.Services.app_stock.articulos.route_codigos import router as codigos_router
from sql_app.Services.app_stock.articulos.route_historial_precios import api_router as historial_api_router
from sql_app.Services.app_stock.articulos.route_historial_precios import router as historial_router
from sql_app.Services.app_stock.articulos_series.route_articulos_series import router as articulos_series_router
from sql_app.Services.app_stock.articulos_tipos.route_articulos_tipos import router as articulos_tipos_router
from sql_app.Services.app_stock.depositos.route_depositos import router as depositos_router
from sql_app.Services.app_stock.depositos_tipos.route_depositos_tipos import router as depositos_tipos_router
from sql_app.Services.app_stock.stock.route_stock import router as stock_router
from sql_app.Services.app_stock.stock.route_stock_admin import router as stock_admin_router
from sql_app.Services.app_stock.stock_historico.route_stock_historico import router as stock_historico_router

# Función para configurar todas las rutas relacionadas con stock
def configure_stock_routes(app: FastAPI):
    """
    Configura todas las rutas relacionadas con el módulo de stock
    
    Args:
        app: Instancia de FastAPI donde se registrarán las rutas
    """
    # Incluir los routers de artículos, historial de precios y códigos
    app.include_router(articulos_router, prefix="/app_stock")
    app.include_router(articulos_tipos_router, prefix="/app_stock")
    app.include_router(articulos_series_router, prefix="/app_stock")

    app.include_router(historial_router, prefix="/app_stock")
    app.include_router(historial_api_router, prefix="/app_stock")  # Incluir el router de API para historial de precios
    app.include_router(codigos_router, prefix="/app_stock")
      # Incluir los routers de stock y depósitos
    app.include_router(stock_admin_router, prefix="/app_stock")
    app.include_router(stock_router, prefix="/app_stock")
    app.include_router(stock_historico_router, prefix="/app_stock")
    app.include_router(depositos_tipos_router, prefix="/app_stock")
    app.include_router(depositos_router, prefix="/app_stock")
    
    
    # Incluir el router de órdenes de trabajo
    app.include_router(ot_router, prefix="/app_stock")
    
    return app