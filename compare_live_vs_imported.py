#!/usr/bin/env python3
"""
Script para comparar las rutas del servidor en vivo vs main.py importado
"""
import requests
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql_app'))

def compare_live_vs_imported():
    print("🔍 COMPARANDO SERVIDOR EN VIVO VS MAIN.PY IMPORTADO")
    print("=" * 60)
    
    # 1. Obtener rutas del servidor en vivo
    print("1. Obteniendo rutas del servidor en vivo...")
    try:
        response = requests.get("http://localhost:8000/openapi.json", timeout=5)
        if response.status_code == 200:
            live_openapi = response.json()
            live_paths = live_openapi.get("paths", {})
            live_activation_routes = [path for path in live_paths.keys() if 'activar' in path]
            print(f"   ✅ Rutas en vivo: {len(live_paths)} total")
            print(f"   Activación en vivo: {live_activation_routes}")
        else:
            print(f"   ❌ Error obteniendo rutas en vivo: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error conectando al servidor: {e}")
        return
    
    # 2. Obtener rutas de main.py importado
    print("\n2. Obteniendo rutas de main.py importado...")
    try:
        import main as main_module
        imported_app = main_module.app
        
        # Contar rutas totales
        imported_total = len(imported_app.routes)
        
        # Buscar rutas de activación
        imported_activation_routes = []
        for route in imported_app.routes:
            if hasattr(route, 'path') and 'activar' in route.path:
                imported_activation_routes.append(route.path)
        
        print(f"   ✅ Rutas importadas: {imported_total} total")
        print(f"   Activación importada: {imported_activation_routes}")
        
    except Exception as e:
        print(f"   ❌ Error importando main.py: {e}")
        return
    
    # 3. Comparar resultados
    print(f"\n3. COMPARACIÓN:")
    print(f"   Rutas en vivo: {len(live_paths)}")
    print(f"   Rutas importadas: {imported_total}")
    print(f"   Diferencia: {imported_total - len(live_paths)}")
    
    print(f"\n   Activación en vivo: {len(live_activation_routes)} - {live_activation_routes}")
    print(f"   Activación importada: {len(imported_activation_routes)} - {imported_activation_routes}")
    
    if len(live_activation_routes) != len(imported_activation_routes):
        print("\n❌ PROBLEMA DETECTADO: Diferentes números de rutas de activación")
        print("   El servidor en vivo NO tiene las rutas de activación")
        print("   Pero main.py importado SÍ las tiene")
        
        # Posibles causas
        print("\n🔍 POSIBLES CAUSAS:")
        print("   1. Working directory diferente")
        print("   2. Error durante el registro del router en uvicorn")
        print("   3. Conflicto de importaciones en el entorno de uvicorn")
        print("   4. Router no registrado debido a algún error silencioso")
        
    else:
        print("\n✅ Ambas instancias tienen el mismo número de rutas de activación")

if __name__ == "__main__":
    compare_live_vs_imported()
