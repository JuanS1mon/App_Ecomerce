#!/usr/bin/env python3
"""
Script para inspeccionar todas las rutas registradas en la aplicación FastAPI
"""
import sys
import os

# Agregar el directorio actual al path para importar
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sql_app'))

def inspect_fastapi_routes():
    """Inspecciona todas las rutas registradas en la aplicación"""
    print("🔍 INSPECCIONANDO RUTAS REGISTRADAS EN FASTAPI")
    print("=" * 60)
    
    try:
        # Importar la aplicación FastAPI
        from sql_app.main import app
        
        print(f"✅ Aplicación cargada exitosamente")
        print(f"📊 Total de rutas registradas: {len(app.routes)}")
        
        # Filtrar rutas relacionadas con login
        login_routes = []
        all_routes = []
        
        for route in app.routes:
            route_info = {
                "path": getattr(route, "path", "N/A"),
                "methods": getattr(route, "methods", ["N/A"]),
                "name": getattr(route, "name", "N/A"),
                "endpoint": getattr(route, "endpoint", "N/A").__name__ if hasattr(getattr(route, "endpoint", None), "__name__") else "N/A"
            }
            
            all_routes.append(route_info)
            
            # Filtrar rutas que contengan "login"
            if "login" in route_info["path"].lower():
                login_routes.append(route_info)
        
        print(f"\n🔐 RUTAS RELACIONADAS CON LOGIN:")
        print("-" * 40)
        
        if login_routes:
            for route in login_routes:
                methods = list(route["methods"]) if route["methods"] != ["N/A"] else ["N/A"]
                print(f"📍 {route['path']}")
                print(f"   Métodos: {methods}")
                print(f"   Nombre: {route['name']}")
                print(f"   Endpoint: {route['endpoint']}")
                print()
        else:
            print("❌ No se encontraron rutas con 'login' en el path")
        
        # Buscar rutas exactas para /login
        print(f"\n🎯 RUTAS EXACTAS PARA '/login':")
        print("-" * 30)
        
        exact_login_routes = [r for r in all_routes if r["path"] == "/login"]
        
        if exact_login_routes:
            for route in exact_login_routes:
                methods = list(route["methods"]) if route["methods"] != ["N/A"] else ["N/A"]
                print(f"📍 {route['path']}")
                print(f"   Métodos: {methods}")
                print(f"   Nombre: {route['name']}")
                print(f"   Endpoint: {route['endpoint']}")
                print()
        else:
            print("❌ No se encontraron rutas exactas para '/login'")
        
        # Buscar rutas que puedan estar conflictivas
        print(f"\n⚠️ ANÁLISIS DE CONFLICTOS:")
        print("-" * 25)
        
        path_methods = {}
        for route in all_routes:
            path = route["path"]
            methods = route["methods"] if route["methods"] != ["N/A"] else []
            
            if path not in path_methods:
                path_methods[path] = []
            
            for method in methods:
                if method not in path_methods[path]:
                    path_methods[path].append(method)
        
        # Verificar /login específicamente
        if "/login" in path_methods:
            print(f"📍 /login permite métodos: {path_methods['/login']}")
            
            # Verificar si hay conflictos
            if "GET" in path_methods["/login"] and "POST" in path_methods["/login"]:
                print("⚠️ CONFLICTO DETECTADO: /login tiene tanto GET como POST")
            elif "POST" in path_methods["/login"]:
                print("✅ /login solo tiene POST (correcto)")
            elif "GET" in path_methods["/login"]:
                print("⚠️ /login solo tiene GET (incorrecto para OAuth2)")
        else:
            print("❌ No se encontró /login en el mapeo de rutas")
        
        # Mostrar algunas rutas adicionales para contexto
        print(f"\n📋 OTRAS RUTAS RELEVANTES:")
        print("-" * 25)
        
        relevant_paths = ["/loginpage", "/admin", "/users/me", "/logout"]
        for path in relevant_paths:
            if path in path_methods:
                print(f"📍 {path}: {path_methods[path]}")
        
    except ImportError as e:
        print(f"❌ Error al importar la aplicación: {e}")
        print("Asegúrate de que el servidor esté detenido y las dependencias estén disponibles")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_fastapi_routes()
