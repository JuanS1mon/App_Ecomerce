#!/usr/bin/env python3
"""
Script para analizar paso a paso la importación de main.py y detectar dónde falla
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql_app'))

def analyze_main_import_step_by_step():
    print("🔍 ANALIZANDO IMPORTACIÓN DE MAIN.PY PASO A PASO")
    print("=" * 60)
    
    try:
        print("1. Verificando importaciones individuales...")
        
        # Verificar importación del router de usuarios
        print("   a) Importando router de usuarios...")
        from routers import usuarios as aut_usuario
        print(f"      ✅ Router importado: {len(aut_usuario.router.routes)} rutas")
        
        # Verificar otras importaciones principales
        print("   b) Importando otros routers...")
        from routers import Blog
        from routers.config import Generar, configDB, Migraciones, Analisis, Scraping, usuarios_admin
        from routers.config.Admin import create_admin_router
        print("      ✅ Otros routers importados")
        
        print("2. Importando aplicación principal...")
        from fastapi import FastAPI
        app = FastAPI()
        print("   ✅ App creada")
        
        print("3. Registrando router de usuarios MANUALMENTE...")
        # Registrar solo el router de usuarios para ver si funciona
        app.include_router(aut_usuario.router)
        print("   ✅ Router de usuarios registrado")
        
        # Verificar si las rutas están ahí
        activation_routes = []
        for route in app.routes:
            if hasattr(route, 'path') and 'activar' in route.path:
                methods = getattr(route, 'methods', set())
                activation_routes.append((route.path, list(methods)))
        
        print(f"4. Verificando rutas de activación: {len(activation_routes)} encontradas")
        for path, methods in activation_routes:
            print(f"   ✅ {path} - {methods}")
        
        if activation_routes:
            print("\n✅ El router se registra correctamente paso a paso")
        else:
            print("\n❌ Las rutas no aparecen después del registro manual")
        
        print("\n5. Ahora importando main.py completo para comparar...")
        import main as main_module
        main_app = main_module.app
        
        # Verificar rutas en main_app
        main_activation_routes = []
        for route in main_app.routes:
            if hasattr(route, 'path') and 'activar' in route.path:
                methods = getattr(route, 'methods', set())
                main_activation_routes.append((route.path, list(methods)))
        
        print(f"6. Rutas de activación en main.app: {len(main_activation_routes)}")
        for path, methods in main_activation_routes:
            print(f"   ✅ {path} - {methods}")
        
        if len(main_activation_routes) != len(activation_routes):
            print("\n⚠️ DISCREPANCIA DETECTADA:")
            print(f"   Manual: {len(activation_routes)} rutas")
            print(f"   Main.py: {len(main_activation_routes)} rutas")
        else:
            print("\n✅ Ambas apps tienen el mismo número de rutas de activación")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    analyze_main_import_step_by_step()
