#!/usr/bin/env python3
"""
Script simple para importar la app y verificar rutas
"""
import sys
import os

# Cambiar al directorio correcto
os.chdir('c:/Users/PCJuan/Desktop/sql_app/sql_app')
sys.path.insert(0, os.getcwd())

try:
    print("Importando aplicación...")
    from main import app
    print(f"✅ App importada. Total rutas: {len(app.routes)}")
    
    # Buscar /login
    for route in app.routes:
        if hasattr(route, 'path') and route.path == '/login':
            methods = getattr(route, 'methods', set())
            print(f"✅ /login encontrada - Métodos: {list(methods)}")
            break
    else:
        print("❌ /login NO encontrada")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
