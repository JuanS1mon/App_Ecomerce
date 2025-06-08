#!/usr/bin/env python3
"""
Script para inspeccionar todas las rutas registradas en la aplicación FastAPI
"""
import requests
import sys
import json

def inspect_routes_via_openapi():
    """Inspecciona las rutas usando OpenAPI"""
    try:
        response = requests.get("http://127.0.0.1:8000/openapi.json")
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            
            print("🔍 RUTAS ENCONTRADAS EN OPENAPI:")
            print("=" * 50)
            
            login_routes = []
            admin_routes = []
            
            for path, methods in paths.items():
                print(f"\n📍 {path}:")
                for method, details in methods.items():
                    summary = details.get("summary", "Sin descripción")
                    print(f"   {method.upper()}: {summary}")
                    
                    if "login" in path.lower():
                        login_routes.append((path, method.upper()))
                    if "admin" in path.lower():
                        admin_routes.append((path, method.upper()))
            
            print(f"\n📊 RESUMEN:")
            print(f"   Total rutas: {len(paths)}")
            print(f"   Rutas de login: {len(login_routes)}")
            print(f"   Rutas de admin: {len(admin_routes)}")
            
            if login_routes:
                print(f"\n🔐 RUTAS DE LOGIN ENCONTRADAS:")
                for path, method in login_routes:
                    print(f"   {method} {path}")
            
            if admin_routes:
                print(f"\n🏛️ RUTAS DE ADMIN ENCONTRADAS:")
                for path, method in admin_routes:
                    print(f"   {method} {path}")
                    
            return True
            
    except Exception as e:
        print(f"❌ Error inspeccionando OpenAPI: {str(e)}")
        return False

def manual_route_inspection():
    """Inspección manual de rutas específicas"""
    base_url = "http://127.0.0.1:8000"
    
    print(f"\n🔧 INSPECCIÓN MANUAL DE RUTAS")
    print("=" * 40)
    
    # Probar diferentes combinaciones
    test_routes = [
        ("/login", "OPTIONS"),  # Verificar qué métodos están permitidos
        ("/login", "HEAD"),
        ("/login", "POST"),
        ("/login", "GET"),
    ]
    
    for route, method in test_routes:
        try:
            if method == "OPTIONS":
                response = requests.options(f"{base_url}{route}")
            elif method == "HEAD":
                response = requests.head(f"{base_url}{route}")
            elif method == "POST":
                response = requests.post(f"{base_url}{route}", data={"test": "test"})
            elif method == "GET":
                response = requests.get(f"{base_url}{route}")
            
            print(f"   {method} {route}: {response.status_code}")
            
            # Mostrar headers Allow si están disponibles
            if "allow" in response.headers:
                print(f"      Métodos permitidos: {response.headers['allow']}")
                
        except Exception as e:
            print(f"   {method} {route}: Error - {str(e)}")

def test_with_curl_equivalent():
    """Prueba con una petición equivalente a curl para mayor detalle"""
    print(f"\n🌐 PETICIÓN DETALLADA POST /login")
    print("=" * 40)
    
    try:
        import urllib.parse
        
        # Datos exactamente como OAuth2PasswordRequestForm los espera
        data = urllib.parse.urlencode({
            'username': 'juan',
            'password': '123456'
        })
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': str(len(data)),
            'Accept': 'application/json',
            'User-Agent': 'test-script/1.0'
        }
        
        print(f"URL: http://127.0.0.1:8000/login")
        print(f"Method: POST")
        print(f"Headers: {headers}")
        print(f"Data: {data}")
        
        response = requests.post(
            "http://127.0.0.1:8000/login",
            data=data,
            headers=headers
        )
        
        print(f"\nRespuesta:")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Body: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    print("🔍 INSPECCIÓN COMPLETA DE RUTAS")
    print("=" * 50)
    
    # 1. Verificar OpenAPI
    openapi_success = inspect_routes_via_openapi()
    
    # 2. Inspección manual
    manual_route_inspection()
    
    # 3. Prueba detallada
    login_success = test_with_curl_equivalent()
    
    print(f"\n" + "=" * 50)
    print(f"🏁 RESULTADO FINAL:")
    print(f"   OpenAPI accesible: {'✅' if openapi_success else '❌'}")
    print(f"   Login funcional: {'✅' if login_success else '❌'}")
    
    if not login_success:
        print(f"\n💡 POSIBLES CAUSAS:")
        print(f"   • Conflicto entre rutas GET y POST en /login")
        print(f"   • Error en el registro del router de usuarios")
        print(f"   • Problema con OAuth2PasswordRequestForm")
        print(f"   • Middleware interfiriendo con las rutas")

if __name__ == "__main__":
    main()
