#!/usr/bin/env python3
"""
Test específico para verificar si el router de usuarios está correctamente registrado
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql_app'))

def test_router_registration():
    """Verifica la registración del router de usuarios"""
    print("🔍 VERIFICANDO REGISTRACIÓN DEL ROUTER DE USUARIOS")
    print("=" * 60)
    
    try:
        # Importar la aplicación principal
        from sql_app.main import app
        from sql_app.routers.usuarios import router as usuarios_router
        
        print("✅ Importaciones exitosas")
        
        # Verificar si el router está en la aplicación
        found_router = False
        logout_route_found = False
        login_route_found = False
        
        print(f"\n📊 ANÁLISIS DE RUTAS EN APP:")
        
        for route in app.routes:
            if hasattr(route, 'router') and route.router == usuarios_router:
                found_router = True
                print(f"  ✅ Router de usuarios encontrado en la app")
                break
        
        if not found_router:
            print(f"  ❌ Router de usuarios NO encontrado en la app")
        
        print(f"\n📋 RUTAS ESPECÍFICAS:")
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                if route.path == '/logout':
                    logout_route_found = True
                    methods = list(route.methods)
                    print(f"  ✅ /logout encontrado - Métodos: {methods}")
                elif route.path == '/login':
                    login_route_found = True
                    methods = list(route.methods)
                    print(f"  ✅ /login encontrado - Métodos: {methods}")
        
        if not logout_route_found:
            print(f"  ❌ Ruta /logout NO encontrada")
        if not login_route_found:
            print(f"  ❌ Ruta /login NO encontrada")
        
        # Verificar rutas directamente en el router
        print(f"\n🔄 RUTAS EN EL ROUTER DE USUARIOS:")
        logout_in_router = False
        login_in_router = False
        
        for route in usuarios_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                if route.path == '/logout':
                    logout_in_router = True
                    methods = list(route.methods)
                    print(f"  ✅ /logout en router - Métodos: {methods}")
                elif route.path == '/login':
                    login_in_router = True
                    methods = list(route.methods)
                    print(f"  ✅ /login en router - Métodos: {methods}")
        
        if not logout_in_router:
            print(f"  ❌ /logout NO está en el router de usuarios")
        if not login_in_router:
            print(f"  ❌ /login NO está en el router de usuarios")
        
        # Resultado final
        print(f"\n📋 DIAGNÓSTICO:")
        all_good = found_router and logout_route_found and login_route_found and logout_in_router and login_in_router
        
        if all_good:
            print("✅ Todo parece estar correctamente registrado")
            print("🔍 El problema debe estar en otro lugar")
        else:
            print("❌ Hay problemas en la registración del router")
            
        return all_good
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_router_registration()
