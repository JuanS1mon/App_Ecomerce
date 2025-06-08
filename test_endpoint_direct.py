#!/usr/bin/env python3
"""
Script para probar el endpoint /usuarios/current directamente
"""
import sys
import os
sys.path.insert(0, 'sql_app')

from sql_app.main import app
from fastapi.testclient import TestClient

def test_endpoint():
    """Test directo del endpoint"""
    client = TestClient(app)
    
    print("🔍 Probando /usuarios/current sin token...")
    response = client.get('/usuarios/current')
    print(f"Status: {response.status_code}")
    print(f"Content: {response.text[:200]}")
    
    print("\n🔍 Probando con token inválido...")
    headers = {'Authorization': 'Bearer invalid_token'}
    response = client.get('/usuarios/current', headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Content: {response.text[:200]}")
    
    print("\n🔍 Verificando rutas registradas...")
    for route in app.routes:
        if hasattr(route, 'path') and 'current' in route.path:
            print(f"Ruta encontrada: {route.path} - {route.methods if hasattr(route, 'methods') else 'N/A'}")

if __name__ == "__main__":
    test_endpoint()
