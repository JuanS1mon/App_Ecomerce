#!/usr/bin/env python3
"""
Script para investigar la causa raíz específica del problema de routing POST /login
Sospecha: Conflicto en el orden de registro de rutas o problema con FastAPI/Starlette
"""
import sys
import os
import requests

# Agregar el directorio actual al path para importar
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sql_app'))

def test_direct_route_access():
    """Prueba acceso directo a nivel de ruta"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 INVESTIGACIÓN PROFUNDA DEL PROBLEMA DE ROUTING")
    print("=" * 65)
    
    # 1. Test exhaustivo de métodos HTTP
    methods_to_test = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
    
    print(f"\n📋 PROBANDO TODOS LOS MÉTODOS HTTP EN /login:")
    print("-" * 50)
    
    for method in methods_to_test:
        try:
            response = requests.request(
                method, 
                f"{base_url}/login",
                data={"username": "test", "password": "test"} if method in ['POST', 'PUT', 'PATCH'] else None,
                headers={"Content-Type": "application/x-www-form-urlencoded"} if method in ['POST', 'PUT', 'PATCH'] else {},
                timeout=5
            )
            
            allow_header = response.headers.get('Allow', 'N/A')
            content_type = response.headers.get('Content-Type', 'N/A')
            
            print(f"   {method:8}: Status {response.status_code:3} | Allow: {allow_header:15} | Type: {content_type[:30]}")
            
            if response.status_code == 405:
                print(f"            Body: {response.text[:100]}...")
            
        except Exception as e:
            print(f"   {method:8}: ERROR - {str(e)[:50]}")
    
    return True

def analyze_starlette_router_behavior():
    """Analiza el comportamiento del router interno de Starlette"""
    print(f"\n🔍 ANÁLISIS DEL ROUTER INTERNO DE STARLETTE")
    print("=" * 50)
    
    try:
        from sql_app.main import app
        
        # Encontrar la ruta específica
        login_route = None
        for route in app.routes:
            if hasattr(route, 'path') and route.path == "/login":
                login_route = route
                break
        
        if not login_route:
            print("❌ No se encontró la ruta /login")
            return False
        
        print(f"✅ Ruta /login encontrada:")
        print(f"   Tipo: {type(login_route).__name__}")
        print(f"   Path: {login_route.path}")
        print(f"   Métodos: {getattr(login_route, 'methods', 'N/A')}")
        print(f"   Endpoint: {getattr(login_route, 'endpoint', 'N/A')}")
        
        # Simular el proceso de matching de Starlette
        print(f"\n🔍 SIMULANDO MATCHING DE STARLETTE:")
        
        # Crear un scope simulado para POST
        post_scope = {
            "type": "http",
            "method": "POST",
            "path": "/login",
            "query_string": b"",
            "headers": []
        }
        
        # Crear un scope simulado para GET
        get_scope = {
            "type": "http",
            "method": "GET", 
            "path": "/login",
            "query_string": b"",
            "headers": []
        }
        
        # Probar matching
        from starlette.routing import Match
        
        print(f"   POST /login matching:")
        post_match, post_child_scope = login_route.matches(post_scope)
        print(f"      Resultado: {post_match}")
        print(f"      Child scope: {post_child_scope}")
        
        print(f"   GET /login matching:")
        get_match, get_child_scope = login_route.matches(get_scope)
        print(f"      Resultado: {get_match}")
        print(f"      Child scope: {get_child_scope}")
        
        # Verificar si hay patrones especiales
        if hasattr(login_route, 'path_regex'):
            print(f"   Path regex: {login_route.path_regex.pattern}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_router_registration_order():
    """Verifica el orden de registro de routers"""
    print(f"\n🔍 VERIFICANDO ORDEN DE REGISTRO DE ROUTERS")
    print("=" * 45)
    
    try:
        from sql_app.main import app
        
        print(f"✅ Total de rutas registradas: {len(app.routes)}")
        
        # Buscar todas las rutas que podrían interferir con /login
        potential_conflicts = []
        login_routes = []
        
        for i, route in enumerate(app.routes):
            route_path = getattr(route, 'path', None)
            route_methods = getattr(route, 'methods', set())
            
            if route_path == "/login":
                login_routes.append((i, route, route_methods))
                print(f"   Índice {i:2}: /login - Métodos: {route_methods}")
            
            elif route_path and ('login' in route_path.lower() or route_path.startswith('/log')):
                potential_conflicts.append((i, route_path, route_methods))
        
        print(f"\n📊 RUTAS /login ENCONTRADAS: {len(login_routes)}")
        
        if len(login_routes) > 1:
            print("⚠️ MÚLTIPLES RUTAS /login DETECTADAS!")
            for idx, route, methods in login_routes:
                print(f"   {idx}: {type(route).__name__} - {methods}")
        elif len(login_routes) == 1:
            print("✅ Una sola ruta /login (correcto)")
        else:
            print("❌ No se encontraron rutas /login")
        
        if potential_conflicts:
            print(f"\n🔍 POSIBLES CONFLICTOS DETECTADOS:")
            for idx, path, methods in potential_conflicts:
                print(f"   {idx:2}: {path} - {methods}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_fastapi_route_resolution():
    """Prueba la resolución de rutas de FastAPI específicamente"""
    print(f"\n🔍 PROBANDO RESOLUCIÓN DE RUTAS DE FASTAPI")
    print("=" * 45)
    
    try:
        from sql_app.main import app
        
        # Usar el router interno para resolver rutas
        router = app.router
        
        print(f"✅ Router obtenido: {type(router).__name__}")
        
        # Simular diferentes requests
        test_scopes = [
            {
                "type": "http",
                "method": "POST",
                "path": "/login",
                "query_string": b"",
                "headers": [(b"content-type", b"application/x-www-form-urlencoded")]
            },
            {
                "type": "http", 
                "method": "GET",
                "path": "/login",
                "query_string": b"",
                "headers": []
            },
            {
                "type": "http",
                "method": "OPTIONS",
                "path": "/login", 
                "query_string": b"",
                "headers": []
            }
        ]
        
        for scope in test_scopes:
            method = scope["method"]
            print(f"\n   Probando {method} /login:")
            
            # Buscar coincidencias manualmente
            for route in router.routes:
                if hasattr(route, 'matches'):
                    from starlette.routing import Match
                    match, child_scope = route.matches(scope)
                    
                    if match != Match.NONE and hasattr(route, 'path') and route.path == "/login":
                        print(f"      ✅ Match encontrado: {match}")
                        print(f"      Ruta: {route.path}")
                        print(f"      Métodos: {getattr(route, 'methods', 'N/A')}")
                        print(f"      Endpoint: {getattr(route, 'endpoint', 'N/A')}")
                        break
            else:
                print(f"      ❌ No se encontró match para {method}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar investigación completa"""
    print("🚀 INVESTIGACIÓN COMPLETA DEL PROBLEMA DE ROUTING")
    print("=" * 65)
    
    # 1. Test directo de métodos HTTP
    test1 = test_direct_route_access()
    
    # 2. Análisis del router de Starlette
    test2 = analyze_starlette_router_behavior()
    
    # 3. Verificar orden de registro
    test3 = test_router_registration_order()
    
    # 4. Test resolución FastAPI
    test4 = test_fastapi_route_resolution()
    
    print(f"\n" + "="*65)
    print("📊 RESUMEN DE LA INVESTIGACIÓN")
    print(f"   Test métodos HTTP: {'✅' if test1 else '❌'}")
    print(f"   Análisis Starlette: {'✅' if test2 else '❌'}")
    print(f"   Orden de registro: {'✅' if test3 else '❌'}")
    print(f"   Resolución FastAPI: {'✅' if test4 else '❌'}")

if __name__ == "__main__":
    main()
