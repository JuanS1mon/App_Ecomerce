#!/usr/bin/env python3
"""
Script para diagnosticar el problema del endpoint /usuarios/current
"""
import logging
import sys
import os

# Configurar logging para debug
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_middleware_order():
    """Examinar el orden y configuración de middlewares"""
    print("🔍 DIAGNÓSTICO DE MIDDLEWARE")
    print("=" * 50)
    
    try:
        sys.path.insert(0, 'sql_app')
        from sql_app.main import app
        
        print(f"✅ App cargada correctamente")
        print(f"Middleware stack:")
        
        # Listar middlewares si están disponibles
        if hasattr(app, 'user_middleware'):
            for i, middleware in enumerate(app.user_middleware):
                print(f"   {i+1}. {middleware.cls.__name__}")
                if hasattr(middleware, 'kwargs'):
                    print(f"      Args: {middleware.kwargs}")
        
        # Verificar rutas específicas
        print(f"\n🔍 RUTAS REGISTRADAS:")
        current_routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                print(f"   {route.path} - {getattr(route, 'methods', 'N/A')}")
                if 'current' in route.path:
                    current_routes.append(route)
        
        if current_routes:
            print(f"\n✅ Rutas con 'current' encontradas: {len(current_routes)}")
            for route in current_routes:
                print(f"   - {route.path}")
                print(f"     Métodos: {getattr(route, 'methods', 'N/A')}")
                print(f"     Endpoint: {getattr(route, 'endpoint', 'N/A')}")
        else:
            print(f"\n❌ No se encontraron rutas con 'current'")
    
    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_middleware_order()
