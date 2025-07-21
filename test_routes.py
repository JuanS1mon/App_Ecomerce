#!/usr/bin/env python3
"""Script para probar las rutas de redirección"""

import requests

def test_routes():
    """Probar las rutas de redirección del sistema de obras"""
    print("=== PRUEBA DE RUTAS DE REDIRECCIÓN ===\n")
    
    base_url = "http://127.0.0.1:8000"
    
    # Probar /app_obras (debería redirigir a /app_obras/dashboard)
    print("🔗 Probando /app_obras...")
    try:
        response = requests.get(f"{base_url}/app_obras", allow_redirects=False)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('location', 'N/A')
            print(f"   ✅ Redirecciona a: {location}")
        elif response.status_code == 200:
            print(f"   ✅ Respuesta directa exitosa")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    print()
    
    # Probar /app_obras/dashboard (debería funcionar directamente)
    print("🎯 Probando /app_obras/dashboard...")
    try:
        response = requests.get(f"{base_url}/app_obras/dashboard")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Dashboard accesible directamente")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    print()
    
    # Probar siguiendo redirección
    print("🔄 Probando /app_obras con redirección automática...")
    try:
        response = requests.get(f"{base_url}/app_obras", allow_redirects=True)
        print(f"   Status final: {response.status_code}")
        print(f"   URL final: {response.url}")
        
        if response.status_code == 200:
            print(f"   ✅ Redirección exitosa")
        else:
            print(f"   ❌ Error en redirección")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    print("\n" + "="*50)
    print("RESUMEN:")
    print("• /app_obras → debería redirigir a /app_obras/dashboard")
    print("• /app_obras/dashboard → debería funcionar directamente")
    print("• Ambas URLs deberían mostrar el mismo contenido")

if __name__ == "__main__":
    test_routes()
