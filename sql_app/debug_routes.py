#!/usr/bin/env python3
"""
Script para diagnosticar las rutas de la aplicación FastAPI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main import app
    print("✅ App importada exitosamente")
    
    # Verificar todas las rutas
    print("\n📋 RUTAS REGISTRADAS:")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f"  {route.path} -> {route.methods}")
        elif hasattr(route, 'path'):
            print(f"  {route.path} -> [STATIC/MOUNT]")
    
    # Buscar específicamente la ruta de login
    login_routes = [route for route in app.routes if hasattr(route, 'path') and '/login' in route.path]
    print(f"\n🔍 RUTAS DE LOGIN ENCONTRADAS: {len(login_routes)}")
    for route in login_routes:
        if hasattr(route, 'methods'):
            print(f"  {route.path} -> {route.methods}")
            print(f"    Endpoint: {route.endpoint}")
    
    # Verificar routers incluidos
    print("\n🔧 INFORMACIÓN DE LA APP:")
    print(f"  Título: {app.title}")
    print(f"  Versión: {app.version}")
    print(f"  Total de rutas: {len(app.routes)}")
    
    # Intentar encontrar el router de usuarios
    print("\n🔍 BUSCANDO ROUTER DE USUARIOS:")
    try:
        from routers import usuarios as aut_usuario
        print("✅ Router de usuarios importado exitosamente")
        
        # Verificar las rutas del router
        if hasattr(aut_usuario, 'router'):
            print("✅ Router object encontrado")
            router_routes = aut_usuario.router.routes
            print(f"  Rutas en el router: {len(router_routes)}")
            
            for route in router_routes:
                if hasattr(route, 'path') and hasattr(route, 'methods'):
                    print(f"    {route.path} -> {route.methods}")
                    if '/login' in route.path:
                        print(f"      ⭐ RUTA DE LOGIN ENCONTRADA: {route.endpoint}")
        else:
            print("❌ No se encontró el objeto router")
            
    except Exception as e:
        print(f"❌ Error importando router de usuarios: {e}")
    
    print("\n" + "="*50)
    print("DIAGNÓSTICO COMPLETADO")
    
except Exception as e:
    print(f"❌ Error importando la app: {e}")
    import traceback
    traceback.print_exc()
