#!/usr/bin/env python3
"""
Script específico para diagnosticar el problema del endpoint POST /login
"""
import sys
import os
import requests

# Agregar el directorio al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sql_app'))

def test_server_live():
    """Verificar si el servidor está funcionando y qué devuelve POST /login"""
    print("🔥 PROBANDO SERVIDOR EN VIVO")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Verificar que el servidor responde
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Servidor responde: {response.status_code}")
    except Exception as e:
        print(f"❌ Servidor no responde: {e}")
        return False
    
    # Test 2: OPTIONS /login
    try:
        options_resp = requests.options(f"{base_url}/login", timeout=5)
        print(f"OPTIONS /login: {options_resp.status_code}")
        if "Allow" in options_resp.headers:
            print(f"  Allow: {options_resp.headers['Allow']}")
    except Exception as e:
        print(f"OPTIONS error: {e}")
    
    # Test 3: POST /login
    try:
        post_resp = requests.post(
            f"{base_url}/login",
            data={"username": "test", "password": "test"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5
        )
        print(f"POST /login: {post_resp.status_code}")
        if post_resp.status_code == 405:
            if "Allow" in post_resp.headers:
                print(f"  Allow: {post_resp.headers['Allow']}")
            print("  ❌ Confirmado: Method Not Allowed para POST")
            return False
        elif post_resp.status_code in [200, 401, 422]:
            print("  ✅ POST /login acepta peticiones")
            return True
        else:
            print(f"  ⚠️ Status inesperado: {post_resp.status_code}")
            return False
            
    except Exception as e:
        print(f"POST error: {e}")
        return False

def analyze_app_routes():
    """Analizar las rutas registradas en la aplicación"""
    print("\n🔍 ANALIZANDO RUTAS DE LA APLICACIÓN")
    print("=" * 45)
    
    try:
        from main import app
        print("✅ App importada exitosamente")
        
        # Buscar todas las rutas con /login
        login_routes = []
        all_routes = []
        
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                path = route.path
                methods = list(route.methods) if route.methods else []
                all_routes.append((path, methods))
                
                if 'login' in path.lower():
                    login_routes.append((path, methods))
        
        print(f"📊 Total rutas: {len(all_routes)}")
        print(f"🔍 Rutas con 'login': {len(login_routes)}")
        
        for path, methods in login_routes:
            print(f"  {path} -> {methods}")
            
        # Buscar específicamente POST /login
        post_login_found = False
        for path, methods in login_routes:
            if path == '/login' and 'POST' in methods:
                post_login_found = True
                print("✅ POST /login encontrado en las rutas registradas")
                break
        
        if not post_login_found:
            print("❌ POST /login NO encontrado en las rutas registradas")
            
        return post_login_found
        
    except Exception as e:
        print(f"❌ Error analizando rutas: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_router_import():
    """Verificar si el router de usuarios se importa correctamente"""
    print("\n🔧 VERIFICANDO IMPORTACIÓN DEL ROUTER")
    print("=" * 45)
    
    try:
        from routers.usuarios import router as usuarios_router
        print("✅ Router de usuarios importado")
        
        # Verificar rutas en el router
        login_in_router = False
        router_routes = []
        
        for route in usuarios_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                path = route.path
                methods = list(route.methods) if route.methods else []
                router_routes.append((path, methods))
                
                if path == '/login' and 'POST' in methods:
                    login_in_router = True
        
        print(f"📊 Rutas en router: {len(router_routes)}")
        
        # Mostrar primeras 5 rutas
        print("🔍 Primeras rutas del router:")
        for path, methods in router_routes[:5]:
            print(f"  {path} -> {methods}")
        
        if login_in_router:
            print("✅ POST /login encontrado en el router")
        else:
            print("❌ POST /login NO encontrado en el router")
            
        return login_in_router
        
    except Exception as e:
        print(f"❌ Error importando router: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Diagnóstico completo"""
    print("🔍 DIAGNÓSTICO COMPLETO DEL PROBLEMA POST /login")
    print("=" * 60)
    
    # Cambiar al directorio sql_app
    os.chdir(os.path.join(os.path.dirname(__file__), 'sql_app'))
    
    # Test 1: Servidor en vivo
    server_ok = test_server_live()
    
    # Test 2: Rutas de la aplicación
    routes_ok = analyze_app_routes()
    
    # Test 3: Router de usuarios
    router_ok = check_router_import()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📋 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 60)
    print(f"Servidor acepta POST /login: {'✅' if server_ok else '❌'}")
    print(f"POST /login en app.routes: {'✅' if routes_ok else '❌'}")
    print(f"POST /login en router: {'✅' if router_ok else '❌'}")
    
    if not server_ok and routes_ok and router_ok:
        print("\n🎯 CONCLUSIÓN: El router está bien configurado pero algo impide")
        print("   que el servidor maneje POST requests a /login.")
        print("   Posibles causas:")
        print("   - Middleware interceptando las requests")
        print("   - Orden de registro de routers")
        print("   - Problema de configuración de FastAPI")
    elif not routes_ok:
        print("\n🎯 CONCLUSIÓN: El router no se está registrando correctamente")
        print("   en la aplicación principal.")
    elif not router_ok:
        print("\n🎯 CONCLUSIÓN: El endpoint POST /login no está definido")
        print("   correctamente en el router de usuarios.")
    else:
        print("\n🎯 CONCLUSIÓN: Todo parece estar configurado correctamente.")
        print("   El problema podría estar en otro lugar.")

if __name__ == "__main__":
    main()
