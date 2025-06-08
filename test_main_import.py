#!/usr/bin/env python3
"""
Script para verificar errores durante la importación de main.py
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql_app'))

def test_main_import():
    print("🔍 TESTANDO IMPORTACIÓN DE MAIN.PY")
    print("=" * 50)
    
    try:
        print("1. Importando main...")
        import sql_app.main as main_module
        print("   ✅ main.py importado correctamente")
        
        print(f"2. Verificando app...")
        app = main_module.app
        print(f"   ✅ App disponible: {type(app)}")
        
        print(f"3. Contando rutas registradas...")
        total_routes = len(app.routes)
        print(f"   Total de rutas: {total_routes}")
        
        print(f"4. Buscando rutas de usuarios...")
        user_routes = []
        activation_routes = []
        
        for route in app.routes:
            if hasattr(route, 'path'):
                path = route.path
                if any(keyword in path for keyword in ['login', 'logout', 'usuario']):
                    methods = getattr(route, 'methods', set())
                    user_routes.append((path, list(methods)))
                
                if 'activar' in path:
                    methods = getattr(route, 'methods', set())
                    activation_routes.append((path, list(methods)))
        
        print(f"\n📋 RUTAS DE USUARIOS ENCONTRADAS ({len(user_routes)}):")
        for path, methods in user_routes:
            print(f"   {path} - {methods}")
            
        print(f"\n🎯 RUTAS DE ACTIVACIÓN ENCONTRADAS ({len(activation_routes)}):")
        for path, methods in activation_routes:
            print(f"   {path} - {methods}")
            
        if not activation_routes:
            print("   ❌ No se encontraron rutas de activación")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error durante la importación: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_main_import()
