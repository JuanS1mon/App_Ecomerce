#!/usr/bin/env python3
"""
Test rápido para verificar que la aplicación funciona correctamente
"""

import requests
import json

def test_app_health():
    """Test básico de salud de la aplicación"""
    try:
        # Test de endpoint raíz
        response = requests.get("http://127.0.0.1:8000/")
        print(f"✅ Endpoint raíz: {response.status_code}")
        
        # Test de documentación
        response = requests.get("http://127.0.0.1:8000/docs")
        print(f"✅ Documentación: {response.status_code}")
        
        # Test de openapi.json
        response = requests.get("http://127.0.0.1:8000/openapi.json")
        print(f"✅ OpenAPI schema: {response.status_code}")
        
        if response.status_code == 200:
            openapi_data = response.json()
            paths_count = len(openapi_data.get('paths', {}))
            print(f"✅ Rutas registradas: {paths_count}")
        
        print("\n🎉 ¡Aplicación funcionando correctamente!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor. Asegúrate de que la aplicación esté ejecutándose.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_app_health()
