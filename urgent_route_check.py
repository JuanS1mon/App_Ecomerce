#!/usr/bin/env python3
"""
Script para verificar el estado actual de las rutas después de los cambios
"""

import requests
import sys
import os

def quick_route_check():
    """Verificación rápida del estado de las rutas"""
    base_url = "http://localhost:8000"
    
    print("🚨 VERIFICACIÓN URGENTE DEL ESTADO DE RUTAS")
    print("=" * 60)
    
    # Verificar si el servidor responde
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Servidor responde: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Servidor no responde: {e}")
        return
    
    # Verificar /login con todos los métodos
    methods = ['GET', 'POST', 'OPTIONS', 'PUT', 'DELETE']
    
    print(f"\nEstado actual de /login:")
    for method in methods:
        try:
            response = requests.request(method, f"{base_url}/login", timeout=3)
            allow_header = response.headers.get('Allow', 'No Allow header')
            print(f"{method:7}: Status {response.status_code:3} | Allow: {allow_header}")
        except Exception as e:
            print(f"{method:7}: Error - {e}")
    
    # Verificar otros endpoints para comparar
    print(f"\nComparación con otros endpoints:")
    endpoints = ['/docs', '/admin', '/usuarios/', '/tickets/']
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=3)
            print(f"GET {endpoint}: Status {response.status_code}")
        except Exception as e:
            print(f"GET {endpoint}: Error - {e}")

def check_internal_routes():
    """Verifica las rutas registradas internamente"""
    print(f"\n🔍 VERIFICANDO RUTAS INTERNAS:")
    
    try:
        # Agregar el path de la aplicación
        sys.path.insert(0, 'sql_app')
        
        from sql_app.main import app
        
        # Buscar todas las rutas relacionadas con login
        login_routes = []
        all_routes = []
        
        def inspect_routes(routes, prefix=""):
            """Inspecciona rutas recursivamente"""
            for route in routes:
                route_path = prefix + getattr(route, 'path', 'No path')
                all_routes.append({
                    'path': route_path,
                    'methods': getattr(route, 'methods', 'No methods'),
                    'name': getattr(route, 'name', 'No name'),
                    'type': type(route).__name__
                })
                
                if 'login' in route_path.lower():
                    login_routes.append({
                        'path': route_path,
                        'methods': getattr(route, 'methods', 'No methods'),
                        'name': getattr(route, 'name', 'No name'),
                        'type': type(route).__name__
                    })
                
                # Si es un Mount/Include, inspeccionar subrutas
                if hasattr(route, 'routes'):
                    inspect_routes(route.routes, prefix + route.path)
        
        inspect_routes(app.routes)
        
        print(f"Total de rutas encontradas: {len(all_routes)}")
        print(f"Rutas relacionadas con login: {len(login_routes)}")
        
        if login_routes:
            print("\nRutas de login encontradas:")
            for route in login_routes:
                print(f"  {route['path']} ({route['type']}) - Métodos: {route['methods']}")
        else:
            print("\n❌ NO SE ENCONTRARON RUTAS DE LOGIN")
            
        # Mostrar algunas rutas para verificar que la inspección funciona
        print(f"\nPrimeras 10 rutas registradas:")
        for route in all_routes[:10]:
            print(f"  {route['path']} - {route['methods']}")
            
    except Exception as e:
        print(f"Error al inspeccionar rutas internas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_route_check()
    check_internal_routes()
