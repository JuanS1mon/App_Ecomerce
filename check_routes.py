#!/usr/bin/env python3
"""
Script para verificar las rutas disponibles en el servidor
"""

import requests
import json

def check_routes():
    """Verificar qué rutas están disponibles"""
    
    BASE_URL = "http://localhost:8000"
    
    print("🔍 VERIFICANDO RUTAS DISPONIBLES")
    print("=" * 50)
    
    # Probar endpoints conocidos
    endpoints_to_test = [
        ("GET", "/"),
        ("GET", "/docs"),
        ("GET", "/openapi.json"),
        ("POST", "/login"),
        ("GET", "/loginpage"),
        ("GET", "/admin"),
        ("GET", "/admin-simple"),
    ]
    
    for method, endpoint in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            elif method == "POST":
                # Para POST /login, enviar datos de formulario
                if endpoint == "/login":
                    data = {"username": "testuser", "password": "testpass123"}
                    response = requests.post(
                        f"{BASE_URL}{endpoint}",
                        data=data,
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                        timeout=5
                    )
                else:
                    response = requests.post(f"{BASE_URL}{endpoint}", timeout=5)
            
            status = response.status_code
            content_type = response.headers.get('content-type', 'unknown')
            
            if status < 400:
                print(f"✅ {method} {endpoint}: {status} ({content_type})")
            elif status == 405:
                print(f"❌ {method} {endpoint}: {status} - Method Not Allowed")
            elif status == 404:
                print(f"❓ {method} {endpoint}: {status} - Not Found")
            else:
                print(f"⚠️  {method} {endpoint}: {status} - {response.reason}")
                
            # Si es 405, probar con otros métodos
            if status == 405 and method == "POST":
                print(f"   🔄 Probando GET en su lugar...")
                get_response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
                print(f"   GET {endpoint}: {get_response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {method} {endpoint}: Conexión rechazada - Servidor no está ejecutándose")
        except Exception as e:
            print(f"❌ {method} {endpoint}: Error - {e}")
    
    # Intentar obtener documentación OpenAPI para ver rutas
    print("\n📋 INTENTANDO OBTENER DOCUMENTACIÓN DE RUTAS...")
    try:
        openapi_response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        if openapi_response.status_code == 200:
            openapi_data = openapi_response.json()
            paths = openapi_data.get("paths", {})
            print("Rutas disponibles según OpenAPI:")
            for path, methods in paths.items():
                available_methods = list(methods.keys())
                print(f"   {path}: {', '.join(available_methods).upper()}")
        else:
            print(f"   No se pudo obtener OpenAPI: {openapi_response.status_code}")
    except Exception as e:
        print(f"   Error obteniendo OpenAPI: {e}")

if __name__ == "__main__":
    check_routes()
