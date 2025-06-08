#!/usr/bin/env python3
"""
Test directo del endpoint /usuarios/current para identificar el punto de intercepción
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from sql_app.main import app
import json

def test_current_endpoint_direct():
    """Test directo del endpoint sin middleware HTTP"""
    print("=== TEST DIRECTO DEL ENDPOINT /usuarios/current ===")
    
    client = TestClient(app)
    
    # Test 1: Llamada directa sin token
    print("\n1. Test sin token de autenticación:")
    response = client.get("/usuarios/current")
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    
    # Test 2: Llamada con token de prueba
    print("\n2. Test con token de prueba:")
    test_token = "test_token_123"
    response = client.get("/usuarios/current", headers={"Authorization": f"Bearer {test_token}"})
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    
    # Test 3: Verificar que el endpoint existe en las rutas
    print("\n3. Verificando rutas disponibles:")
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append(f"{list(route.methods)} {route.path}")
    
    current_routes = [r for r in routes if 'current' in r.lower()]
    print("Rutas que contienen 'current':")
    for route in current_routes:
        print(f"  - {route}")
    
    # Test 4: Verificar rutas de usuarios
    usuarios_routes = [r for r in routes if 'usuarios' in r.lower()]
    print("\nRutas que contienen 'usuarios':")
    for route in usuarios_routes:
        print(f"  - {route}")
    
    return response

if __name__ == "__main__":
    try:
        result = test_current_endpoint_direct()
        print(f"\n=== RESULTADO FINAL ===")
        print(f"El endpoint {'EXISTE' if result.status_code != 404 else 'NO EXISTE'}")
        print(f"Status Code: {result.status_code}")
        
    except Exception as e:
        print(f"ERROR durante el test: {e}")
        import traceback
        traceback.print_exc()
