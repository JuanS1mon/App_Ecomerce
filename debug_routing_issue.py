#!/usr/bin/env python3
"""
Script para diagnosticar el problema específico del routing en FastAPI
donde POST /login retorna 405 con "Allow: GET" pero debería ser POST.
"""
import sys
import os
import requests
from typing import Dict, List

# Agregar el directorio actual al path para importar
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sql_app'))

def test_live_server():
    """Prueba el servidor en vivo para confirmar el problema"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 DIAGNOSTICANDO EL PROBLEMA DE ROUTING EN VIVO")
    print("=" * 60)
    
    # 1. Verificar servidor
    try:
        health = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Servidor responde: {health.status_code}")
    except Exception as e:
        print(f"❌ Servidor no responde: {e}")
        return False
    
    # 2. Probar OPTIONS
    print(f"\n📋 TEST 1: OPTIONS /login")
    try:
        options_resp = requests.options(f"{base_url}/login")
        print(f"   Status: {options_resp.status_code}")
        print(f"   Allow header: {options_resp.headers.get('Allow', 'N/A')}")
        print(f"   All headers: {dict(options_resp.headers)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 3. Probar POST
    print(f"\n📋 TEST 2: POST /login")
    try:
        login_data = {"username": "juan", "password": "123456"}
        post_resp = requests.post(
            f"{base_url}/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"   Status: {post_resp.status_code}")
        print(f"   Allow header: {post_resp.headers.get('Allow', 'N/A')}")
        print(f"   Content-Type: {post_resp.headers.get('Content-Type', 'N/A')}")
        print(f"   Response: {post_resp.text[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 4. Probar GET para comparación
    print(f"\n📋 TEST 3: GET /login")
    try:
        get_resp = requests.get(f"{base_url}/login")
        print(f"   Status: {get_resp.status_code}")
        print(f"   Allow header: {get_resp.headers.get('Allow', 'N/A')}")
        print(f"   Content-Type: {get_resp.headers.get('Content-Type', 'N/A')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    return True

def analyze_route_registration():
    """Analiza cómo está registrada la ruta en el código"""
    print(f"\n🔍 ANALIZANDO REGISTRO DE RUTAS")
    print("=" * 40)
    
    try:
        # Importar sin iniciar el servidor
        from sql_app.main import app
        
        print(f"✅ App importada exitosamente")
        
        # Buscar la ruta /login específicamente
        login_routes = []
        
        def analyze_route(route, level=0):
            """Función recursiva para analizar rutas anidadas"""
            indent = "  " * level
            
            if hasattr(route, 'path') and route.path == "/login":
                route_info = {
                    "path": route.path,
                    "methods": getattr(route, 'methods', None),
                    "endpoint": getattr(route, 'endpoint', None),
                    "router": getattr(route, 'router', None),
                    "name": getattr(route, 'name', None),
                    "route_type": type(route).__name__
                }
                login_routes.append(route_info)
                print(f"{indent}📍 Encontrada ruta /login:")
                print(f"{indent}   Tipo: {route_info['route_type']}")
                print(f"{indent}   Métodos: {route_info['methods']}")
                print(f"{indent}   Endpoint: {route_info['endpoint']}")
                print(f"{indent}   Router: {route_info['router']}")
            
            # Si es un Mount, analizar las rutas internas
            if hasattr(route, 'routes'):
                for subroute in route.routes:
                    analyze_route(subroute, level + 1)
            elif hasattr(route, 'app') and hasattr(route.app, 'routes'):
                for subroute in route.app.routes:
                    analyze_route(subroute, level + 1)
        
        # Analizar todas las rutas
        for route in app.routes:
            analyze_route(route)
        
        if not login_routes:
            print("❌ No se encontró ninguna ruta /login registrada")
            return False
        
        print(f"\n📊 RESUMEN:")
        print(f"   Total rutas /login encontradas: {len(login_routes)}")
        
        # Verificar si hay duplicados o conflictos
        methods_found = set()
        for route in login_routes:
            if route['methods']:
                methods_found.update(route['methods'])
        
        print(f"   Métodos combinados: {list(methods_found)}")
        
        if len(login_routes) > 1:
            print("⚠️ MÚLTIPLES RUTAS /login DETECTADAS:")
            for i, route in enumerate(login_routes):
                print(f"   {i+1}. {route['route_type']} - Métodos: {route['methods']}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error al importar app: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_middleware_interference():
    """Verifica si algún middleware está interfiriendo"""
    print(f"\n🔍 VERIFICANDO MIDDLEWARE QUE PUEDA INTERFERIR")
    print("=" * 50)
    
    try:
        from sql_app.main import app
        
        print(f"✅ Middleware stack:")
        
        if hasattr(app, 'user_middleware'):
            for i, middleware in enumerate(app.user_middleware):
                print(f"   {i+1}. {middleware.cls.__name__}")
                if hasattr(middleware, 'options'):
                    print(f"      Opciones: {middleware.options}")
        else:
            print("   No se encontró información de middleware")
        
        # Verificar si hay middleware de CORS problemático
        cors_middleware = [m for m in app.user_middleware if 'CORS' in m.cls.__name__]
        if cors_middleware:
            print(f"\n🌐 CORS Middleware detectado:")
            for cors in cors_middleware:
                print(f"   {cors.cls.__name__}")
                if hasattr(cors, 'options'):
                    options = cors.options
                    allow_methods = options.get('allow_methods', [])
                    print(f"   Allow methods: {allow_methods}")
                    if 'POST' not in allow_methods and '*' not in allow_methods:
                        print("   ⚠️ POST no está explícitamente permitido en CORS")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando middleware: {e}")
        return False

def main():
    """Ejecutar diagnóstico completo"""
    print("🚀 DIAGNÓSTICO COMPLETO DEL PROBLEMA DE ROUTING")
    print("=" * 65)
    
    # 1. Probar servidor en vivo
    server_ok = test_live_server()
    
    if server_ok:
        print(f"\n" + "="*65)
        
        # 2. Analizar registro de rutas
        registration_ok = analyze_route_registration()
        
        # 3. Verificar middleware
        middleware_ok = check_middleware_interference()
        
        print(f"\n" + "="*65)
        print("📊 DIAGNÓSTICO COMPLETADO")
        print(f"   Servidor responde: {'✅' if server_ok else '❌'}")
        print(f"   Rutas registradas: {'✅' if registration_ok else '❌'}")
        print(f"   Middleware OK: {'✅' if middleware_ok else '❌'}")
        
        if server_ok and registration_ok:
            print(f"\n💡 EL PROBLEMA ES DE ROUTING INTERNO")
            print("   La ruta está registrada correctamente pero el router")
            print("   de Starlette no la está resolviendo para POST.")
            print("   Esto puede ser por:")
            print("   1. Conflicto entre múltiples rutas /login")
            print("   2. Middleware que modifica las respuestas")
            print("   3. Problema en el orden de registro de rutas")
            print("   4. Bug específico de versión de FastAPI/Starlette")
    
if __name__ == "__main__":
    main()
