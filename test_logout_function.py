#!/usr/bin/env python3
"""
Prueba directa del endpoint logout sin pasar por FastAPI
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql_app'))

def test_logout_function_directly():
    """Prueba la función logout directamente"""
    print("🔍 PROBANDO FUNCIÓN LOGOUT DIRECTAMENTE")
    print("=" * 50)
    
    try:
        # Importar directamente la función de logout
        from sql_app.routers.usuarios import router
        
        # Buscar la función logout en el router
        logout_route = None
        for route in router.routes:
            if hasattr(route, 'path') and route.path == '/logout':
                logout_route = route
                break
        
        if logout_route:
            print(f"✅ Ruta /logout encontrada")
            print(f"   Métodos: {list(logout_route.methods)}")
            print(f"   Endpoint: {logout_route.endpoint}")
            print(f"   Endpoint nombre: {logout_route.endpoint.__name__ if hasattr(logout_route.endpoint, '__name__') else 'N/A'}")
            
            # Verificar que la función existe y es callable
            if callable(logout_route.endpoint):
                print(f"✅ Función logout es callable")
            else:
                print(f"❌ Función logout NO es callable")
                
        else:
            print(f"❌ Ruta /logout NO encontrada en el router")
            
        # Listar todas las rutas para comparar
        print(f"\n📋 TODAS LAS RUTAS EN EL ROUTER:")
        for route in router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  {route.path} -> {list(route.methods)} -> {route.endpoint.__name__ if hasattr(route.endpoint, '__name__') else 'N/A'}")
        
        return logout_route is not None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_logout_function_directly()
