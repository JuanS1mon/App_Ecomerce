#!/usr/bin/env python3
"""
Script para diagnosticar exactamente por qué /login no funciona
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql_app'))

def diagnose_login_issue():
    print("🔍 DIAGNÓSTICO ESPECÍFICO DEL PROBLEMA /login")
    print("=" * 55)
    
    try:
        print("1. Importando la aplicación...")
        from sql_app.main import app
        print("   ✅ App importada correctamente")
        print(f"   Total rutas: {len(app.routes)}")
        
        print("\n2. Buscando rutas que contienen 'login'...")
        login_routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                if 'login' in route.path.lower():
                    methods = getattr(route, 'methods', set())
                    login_routes.append((route.path, list(methods)))
                    print(f"   ✅ {route.path} - {list(methods)}")
        
        if not login_routes:
            print("   ❌ NO se encontraron rutas con 'login'")
        
        print("\n3. Verificando específicamente la ruta /login...")
        login_route_found = False
        for route in app.routes:
            if hasattr(route, 'path') and route.path == '/login':
                login_route_found = True
                methods = getattr(route, 'methods', set())
                endpoint = getattr(route, 'endpoint', None)
                print(f"   ✅ /login encontrada - Métodos: {list(methods)}")
                print(f"   Endpoint: {endpoint}")
                print(f"   Tipo de ruta: {type(route).__name__}")
                break
        
        if not login_route_found:
            print("   ❌ Ruta /login NO encontrada")
            
        print("\n4. Verificando el router de usuarios directamente...")
        from sql_app.routers.usuarios import router as usuarios_router
        print(f"   ✅ Router importado - {len(usuarios_router.routes)} rutas")
        
        login_in_router = False
        for route in usuarios_router.routes:
            if hasattr(route, 'path') and route.path == '/login':
                login_in_router = True
                methods = getattr(route, 'methods', set())
                print(f"   ✅ /login en router - Métodos: {list(methods)}")
                break
        
        if not login_in_router:
            print("   ❌ /login NO está en el router de usuarios")
            
        print("\n5. Verificando OpenAPI schema...")
        openapi_schema = app.openapi()
        paths = openapi_schema.get('paths', {})
        
        if '/login' in paths:
            methods = list(paths['/login'].keys())
            print(f"   ✅ /login en OpenAPI - Métodos: {methods}")
        else:
            print("   ❌ /login NO está en OpenAPI schema")
            
        # Listar algunas rutas para comparar
        print(f"\n6. Primeras 10 rutas registradas:")
        for i, route in enumerate(app.routes[:10]):
            if hasattr(route, 'path'):
                methods = getattr(route, 'methods', set())
                print(f"   {i+1:2}. {route.path} - {list(methods)}")
                
        return login_route_found and login_in_router
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = diagnose_login_issue()
    
    print("\n" + "=" * 55)
    if success:
        print("✅ La ruta /login está configurada correctamente")
        print("🔍 El problema debe estar en el servidor o middleware")
    else:
        print("❌ Hay un problema con la configuración de la ruta /login")
