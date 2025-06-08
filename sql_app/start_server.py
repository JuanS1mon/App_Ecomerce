#!/usr/bin/env python3
"""
Servidor de prueba para verificar el funcionamiento del login
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    
    # Importar la app
    try:
        from main import app
        print("✅ App importada exitosamente")
        
        # Verificar que el endpoint de login existe
        login_routes = [route for route in app.routes if hasattr(route, 'path') and '/login' in route.path and hasattr(route, 'methods') and 'POST' in route.methods]
        print(f"📋 Rutas de login encontradas: {len(login_routes)}")
        for route in login_routes:
            print(f"  {route.path} -> {route.methods}")        # Iniciar servidor
        print("🚀 Iniciando servidor...")
        uvicorn.run(app, host="0.0.0.0", port=8001)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
