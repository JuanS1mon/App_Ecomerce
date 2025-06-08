#!/usr/bin/env python3
"""
Script para probar los endpoints de activación después del fix
"""
import requests
import json

def test_activation_endpoints():
    print("🔍 PROBANDO ENDPOINTS DE ACTIVACIÓN")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        # Probar endpoint de página de activación
        print("1. Probando GET /activar...")
        response = requests.get(f"{base_url}/activar?token=test_token", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Endpoint funciona - devuelve HTML")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    try:
        # Probar endpoint API de activación
        print("\n2. Probando POST /api/activar...")
        test_data = {"token": "test_token"}
        response = requests.post(
            f"{base_url}/api/activar",
            json=test_data,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 400]:  # 400 esperado por token inválido
            print("   ✅ Endpoint funciona")
            try:
                result = response.json()
                print(f"   Response: {result}")
            except:
                print(f"   Response text: {response.text[:200]}...")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # Verificar OpenAPI schema
    try:
        print("\n3. Verificando OpenAPI schema...")
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if response.status_code == 200:
            openapi_data = response.json()
            paths = openapi_data.get("paths", {})
            
            activation_routes = [path for path in paths.keys() if 'activar' in path]
            if activation_routes:
                print(f"   ✅ Rutas de activación en schema: {activation_routes}")
            else:
                print("   ❌ No se encontraron rutas de activación en schema")
        else:
            print(f"   ❌ Error obteniendo schema: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_activation_endpoints()
