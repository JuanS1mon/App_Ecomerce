#!/usr/bin/env python3
"""
Script para verificar qué rutas están actualmente registradas en el servidor
"""
import requests
import json

def check_server_routes():
    print("🔍 VERIFICANDO RUTAS DEL SERVIDOR")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Verificar si el servidor está corriendo
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        print(f"✅ Servidor está corriendo (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Servidor no está corriendo: {e}")
        return
    
    # Probar diferentes endpoints para ver cuáles funcionan
    endpoints_to_test = [
        "/activar",
        "/api/activar", 
        "/login",
        "/logout",
        "/docs",
        "/openapi.json"
    ]
    
    print(f"\n📋 PROBANDO ENDPOINTS:")
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=3)
            print(f"  ✅ {endpoint} - Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {endpoint} - Error: {e}")
    
    # Obtener schema OpenAPI para ver todas las rutas registradas
    try:
        print(f"\n🔍 OBTENIENDO SCHEMA OPENAPI:")
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if response.status_code == 200:
            openapi_data = response.json()
            paths = openapi_data.get("paths", {})
            
            print(f"Total de rutas registradas: {len(paths)}")
            
            # Buscar rutas relacionadas con activación
            activation_routes = []
            for path, methods in paths.items():
                if 'activar' in path.lower():
                    activation_routes.append((path, list(methods.keys())))
            
            if activation_routes:
                print(f"\n🎯 RUTAS DE ACTIVACIÓN ENCONTRADAS:")
                for path, methods in activation_routes:
                    print(f"  {path} - Métodos: {methods}")
            else:
                print(f"\n❌ NO SE ENCONTRARON RUTAS DE ACTIVACIÓN")
                
            # Mostrar algunas rutas disponibles
            print(f"\n📋 PRIMERAS 10 RUTAS REGISTRADAS:")
            for i, (path, methods) in enumerate(list(paths.items())[:10]):
                print(f"  {i+1}. {path} - {list(methods.keys())}")
                
        else:
            print(f"Error obteniendo OpenAPI schema: {response.status_code}")
    except Exception as e:
        print(f"Error obteniendo schema: {e}")

if __name__ == "__main__":
    check_server_routes()
