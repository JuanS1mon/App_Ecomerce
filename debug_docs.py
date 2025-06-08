#!/usr/bin/env python3
"""
Script para debuggear el problema con el endpoint /docs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sql_app.main import app

def inspect_routes():
    """Inspecciona todas las rutas registradas en la aplicación FastAPI"""
    print("=== RUTAS REGISTRADAS EN FASTAPI ===")
    
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = getattr(route, 'methods', ['GET'])
            print(f"Ruta: {route.path} - Métodos: {list(methods)}")
    
    print("\n=== CONFIGURACIÓN DE DOCUMENTACIÓN ===")
    print(f"docs_url: {app.docs_url}")
    print(f"redoc_url: {app.redoc_url}")
    print(f"openapi_url: {app.openapi_url}")
    
    print("\n=== VARIABLES DE ENTORNO ===")
    from dotenv import load_dotenv
    load_dotenv()
    print(f"ENVIRONMENT: {os.getenv('ENVIRONMENT', 'development')}")

if __name__ == "__main__":
    inspect_routes()
