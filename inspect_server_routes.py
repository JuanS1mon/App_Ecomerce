#!/usr/bin/env python3
"""
Inspeccionar rutas registradas en el servidor FastAPI
"""

import requests
from pprint import pprint

def inspect_server_routes():
    """Inspecciona las rutas disponibles en el servidor"""
    base_url = "http://127.0.0.1:8000"
    
    # Intentar obtener los docs de OpenAPI
    try:
        print("🔍 Obteniendo esquema OpenAPI...")
        openapi_response = requests.get(f"{base_url}/openapi.json")
        
        if openapi_response.status_code == 200:
            openapi_data = openapi_response.json()
            
            print("\n📋 Rutas registradas en el servidor:")
            paths = openapi_data.get("paths", {})
            
            for path, methods in paths.items():
                if "usuarios/current" in path:
                    print(f"🎯 ENCONTRADO: {path}")
                    for method, details in methods.items():
                        print(f"   {method.upper()}: {details.get('summary', 'Sin descripción')}")
                        print(f"   🔑 Seguridad: {details.get('security', 'Sin autenticación')}")
                
                print(f"   {path}: {list(methods.keys())}")
        else:
            print(f"❌ No se pudo obtener OpenAPI: {openapi_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error obteniendo OpenAPI: {str(e)}")
    
    # Probar directamente el endpoint con diferentes métodos
    print("\n🔍 Probando endpoint /usuarios/current directamente...")
    
    endpoints_to_test = [
        "/usuarios/current",
        "/current",
        "/api/usuarios/current",
        "/user/current"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code != 404:
                print(f"✅ ENCONTRADO: {endpoint} -> {response.status_code}")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   📦 Datos: {data}")
                    except:
                        print(f"   📦 Texto: {response.text[:100]}")
        except Exception as e:
            print(f"❌ Error probando {endpoint}: {str(e)}")

if __name__ == "__main__":
    inspect_server_routes()
