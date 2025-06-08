#!/usr/bin/env python3
"""
Script para debuggear la importación del router de usuarios
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql_app'))

def debug_router_import():
    print("🔍 DEBUGGEANDO IMPORTACIÓN DEL ROUTER")
    print("=" * 50)
    
    try:
        print("1. Intentando importar el router...")
        from sql_app.routers import usuarios as aut_usuario
        print("✅ Router importado correctamente")
        
        print(f"\n2. Información del router:")
        print(f"   Tipo: {type(aut_usuario.router)}")
        print(f"   Rutas: {len(aut_usuario.router.routes)}")
        
        print(f"\n3. Primeras 10 rutas:")
        for i, route in enumerate(aut_usuario.router.routes[:10]):
            if hasattr(route, 'path'):
                methods = getattr(route, 'methods', 'No methods')
                print(f"   {i+1}. {route.path} - {methods}")
        
        print(f"\n4. Buscando ruta de activación:")
        activation_found = False
        for route in aut_usuario.router.routes:
            if hasattr(route, 'path') and 'activar' in route.path:
                methods = getattr(route, 'methods', 'No methods')
                print(f"   ✅ {route.path} - {methods}")
                activation_found = True
        
        if not activation_found:
            print("   ❌ No se encontró ruta de activación")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_router_import()
