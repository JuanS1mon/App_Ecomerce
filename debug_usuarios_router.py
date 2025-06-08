#!/usr/bin/env python3
"""
Script para debuggear exactamente qué pasa con el router de usuarios
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql_app'))

def debug_usuarios_router():
    print("🔍 DEBUGGEANDO ROUTER DE USUARIOS")
    print("=" * 50)
    
    try:
        print("1. Importando FastAPI básico...")
        from fastapi import FastAPI, APIRouter
        print("   ✅ FastAPI importado")
        
        print("2. Intentando importar router de usuarios directamente...")
        # Importar el router de usuarios directamente
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sql_app'))
        from routers.usuarios import router as usuarios_router
        print("   ✅ Router de usuarios importado correctamente")
        print(f"   Tipo: {type(usuarios_router)}")
        print(f"   Rutas: {len(usuarios_router.routes)}")
        
        print("3. Verificando rutas de activación en el router...")
        activation_routes = []
        for route in usuarios_router.routes:
            if hasattr(route, 'path') and 'activar' in route.path:
                methods = getattr(route, 'methods', set())
                activation_routes.append((route.path, list(methods)))
                print(f"   ✅ {route.path} - {list(methods)}")
        
        if not activation_routes:
            print("   ❌ No se encontraron rutas de activación en el router")
            return False
        
        print("4. Creando app de prueba y registrando router...")
        test_app = FastAPI()
        test_app.include_router(usuarios_router)
        print("   ✅ Router registrado en app de prueba")
        
        print("5. Verificando rutas en app de prueba...")
        test_activation_routes = []
        for route in test_app.routes:
            if hasattr(route, 'path') and 'activar' in route.path:
                methods = getattr(route, 'methods', set())
                test_activation_routes.append((route.path, list(methods)))
                print(f"   ✅ {route.path} - {list(methods)}")
        
        if test_activation_routes:
            print("   ✅ Rutas de activación registradas correctamente en app de prueba")
            return True
        else:
            print("   ❌ Las rutas no se registraron en la app de prueba")
            return False
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_usuarios_router()
    if success:
        print("\n✅ El router funciona correctamente en aislamiento")
        print("🔍 El problema debe estar en main.py o en el entorno de ejecución")
    else:
        print("\n❌ Hay un problema con el router de usuarios")
