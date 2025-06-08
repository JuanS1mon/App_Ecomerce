#!/usr/bin/env python3
"""
Script para investigar interceptación de métodos HTTP en FastAPI
Busca middleware, hooks o configuraciones que puedan estar modificando los métodos
"""

import requests
import json
from typing import Dict, Any

def test_http_method_interception():
    """Prueba detallada de interceptación de métodos HTTP"""
    base_url = "http://localhost:8000"
    
    print("🔍 INVESTIGANDO INTERCEPTACIÓN DE MÉTODOS HTTP")
    print("=" * 60)
    
    # Test 1: Comparar con otro endpoint POST conocido
    print("\n1. COMPARANDO CON OTROS ENDPOINTS POST:")
    
    # Buscar otros endpoints POST para comparar
    other_post_endpoints = [
        "/usuarios/",  # Crear usuario
        "/tickets/",   # Crear ticket
        "/reset-password/", # Reset password
    ]
    
    for endpoint in other_post_endpoints:
        try:
            response = requests.post(f"{base_url}{endpoint}", json={}, timeout=5)
            print(f"POST {endpoint}: Status {response.status_code}, Allow: {response.headers.get('Allow', 'No header')}")
        except Exception as e:
            print(f"POST {endpoint}: Error - {e}")
    
    # Test 2: Verificar headers específicos de /login
    print("\n2. ANÁLISIS DETALLADO DE HEADERS /login:")
    
    methods_to_test = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
    
    for method in methods_to_test:
        try:
            response = requests.request(method, f"{base_url}/login", timeout=5)
            headers_info = {
                'Allow': response.headers.get('Allow', 'No header'),
                'Content-Type': response.headers.get('Content-Type', 'No header'),
                'Server': response.headers.get('Server', 'No header'),
            }
            print(f"{method:7} /login: Status {response.status_code:3} | Headers: {headers_info}")
        except Exception as e:
            print(f"{method:7} /login: Error - {e}")
    
    # Test 3: Verificar si hay redirecciones o reescrituras
    print("\n3. VERIFICANDO REDIRECCIONES Y REESCRITURAS:")
    
    try:
        # Test con allow_redirects=False para detectar redirecciones
        response = requests.post(f"{base_url}/login", allow_redirects=False, timeout=5)
        print(f"POST /login (sin seguir redirecciones): Status {response.status_code}")
        if 'Location' in response.headers:
            print(f"  Redirección a: {response.headers['Location']}")
        
        # Revisar historial de redirecciones
        response_with_redirects = requests.post(f"{base_url}/login", timeout=5)
        if response_with_redirects.history:
            print(f"  Historial de redirecciones: {len(response_with_redirects.history)} redirecciones")
            for i, redirect in enumerate(response_with_redirects.history):
                print(f"    {i+1}. {redirect.status_code} -> {redirect.headers.get('Location', 'Unknown')}")
        
    except Exception as e:
        print(f"Error en test de redirecciones: {e}")
    
    # Test 4: Verificar headers de CORS
    print("\n4. VERIFICANDO HEADERS DE CORS:")
    
    try:
        # Preflight request simulado
        headers = {
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type',
            'Origin': 'http://localhost:3000'
        }
        response = requests.options(f"{base_url}/login", headers=headers, timeout=5)
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin', 'No header'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods', 'No header'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers', 'No header'),
        }
        print(f"CORS Preflight: Status {response.status_code}")
        for header, value in cors_headers.items():
            print(f"  {header}: {value}")
            
    except Exception as e:
        print(f"Error en test de CORS: {e}")
    
    # Test 5: Verificar comportamiento con diferentes Content-Types
    print("\n5. VERIFICANDO DIFERENTES CONTENT-TYPES:")
    
    content_types = [
        'application/json',
        'application/x-www-form-urlencoded',
        'multipart/form-data',
        'text/plain'
    ]
    
    for content_type in content_types:
        try:
            headers = {'Content-Type': content_type}
            response = requests.post(f"{base_url}/login", headers=headers, timeout=5)
            print(f"POST /login ({content_type}): Status {response.status_code}, Allow: {response.headers.get('Allow', 'No header')}")
        except Exception as e:
            print(f"POST /login ({content_type}): Error - {e}")

def investigate_fastapi_internals():
    """Investiga la configuración interna de FastAPI"""
    print("\n\n🔧 INVESTIGANDO CONFIGURACIÓN INTERNA DE FASTAPI")
    print("=" * 60)
    
    try:
        # Importar los módulos necesarios
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'sql_app'))
        
        from sql_app.main import app
        
        # Verificar middlewares registrados
        print("\n1. MIDDLEWARES REGISTRADOS:")
        for middleware in app.user_middleware:
            print(f"  - {middleware.cls.__name__}: {middleware.args}")
        
        # Verificar rutas registradas específicamente para /login
        print("\n2. RUTAS /login REGISTRADAS:")
        for route in app.routes:
            if hasattr(route, 'path') and route.path == '/login':
                print(f"  - Ruta: {route.path}")
                print(f"    Métodos: {getattr(route, 'methods', 'No methods')}")
                print(f"    Endpoint: {getattr(route, 'endpoint', 'No endpoint')}")
                print(f"    Nombre: {getattr(route, 'name', 'No name')}")
        
        # Verificar subrutas (routers incluidos)
        print("\n3. ROUTERS INCLUIDOS:")
        for route in app.routes:
            if hasattr(route, 'routes'):  # Es un Mount/Include
                print(f"  Router: {route.path}")
                for subroute in route.routes:
                    if hasattr(subroute, 'path') and subroute.path == '/login':
                        print(f"    - Subruta /login encontrada")
                        print(f"      Métodos: {getattr(subroute, 'methods', 'No methods')}")
        
    except Exception as e:
        print(f"Error al investigar internos de FastAPI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        test_http_method_interception()
        investigate_fastapi_internals()
        
        print("\n\n📋 RESUMEN DE INVESTIGACIÓN:")
        print("=" * 60)
        print("1. Compara comportamiento de /login con otros endpoints POST")
        print("2. Analiza headers específicos para todos los métodos HTTP")
        print("3. Verifica redirecciones y reescrituras de URL")
        print("4. Examina configuración de CORS")
        print("5. Prueba diferentes Content-Types")
        print("6. Investiga configuración interna de FastAPI")
        
    except KeyboardInterrupt:
        print("\n\nPrueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n\nError general: {e}")
        import traceback
        traceback.print_exc()
