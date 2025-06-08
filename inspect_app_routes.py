#!/usr/bin/env python3
"""
Script para inspeccionar las rutas registradas en FastAPI desde el interior
"""

import sys
import os

# Añadir el directorio de la aplicación al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql_app'))

try:
    from sql_app.main import app
    
    print("🔍 RUTAS REGISTRADAS EN FASTAPI")
    print("=" * 50)
    
    logout_routes = []
    login_routes = []
    all_routes = []
    
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            path = route.path
            methods = list(route.methods) if route.methods else ['N/A']
            all_routes.append((path, methods))
            
            if 'logout' in path.lower():
                logout_routes.append((path, methods))
            if 'login' in path.lower():
                login_routes.append((path, methods))
    
    print(f"\n📊 TOTAL DE RUTAS: {len(all_routes)}")
    
    print(f"\n🔐 RUTAS DE LOGIN:")
    if login_routes:
        for path, methods in login_routes:
            print(f"  {path} -> {methods}")
    else:
        print("  No se encontraron rutas de login")
    
    print(f"\n🚪 RUTAS DE LOGOUT:")
    if logout_routes:
        for path, methods in logout_routes:
            print(f"  {path} -> {methods}")
    else:
        print("  No se encontraron rutas de logout")
    
    print(f"\n📋 TODAS LAS RUTAS RELEVANTES:")
    relevant_paths = ['/login', '/logout', '/loginpage', '/admin', '/users/me', '/usuarios/current']
    for path, methods in all_routes:
        if any(rel in path for rel in relevant_paths):
            print(f"  {path} -> {methods}")
            
    print(f"\n🔄 VERIFICANDO ROUTER DE USUARIOS:")
    # Intentar importar el router directamente
    try:
        from sql_app.routers.usuarios import router as usuarios_router
        print(f"  ✅ Router importado correctamente")
        print(f"  📝 Rutas en el router:")
        for route in usuarios_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"    {route.path} -> {list(route.methods)}")
    except Exception as e:
        print(f"  ❌ Error importando router: {e}")

except Exception as e:
    print(f"❌ Error importando la aplicación: {e}")
    import traceback
    traceback.print_exc()
