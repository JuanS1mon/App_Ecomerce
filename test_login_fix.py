#!/usr/bin/env python3
"""
Test para verificar si el login funciona correctamente después del fix
"""
import requests
import json

def test_login_endpoint():
    """Probar el endpoint de login"""
    print("🔍 PROBANDO ENDPOINT DE LOGIN")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    
    # Datos de login
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    print(f"1. Probando POST {base_url}/login...")
    
    try:
        # Probar POST /login con form data
        response = requests.post(
            f"{base_url}/login",
            data=login_data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("   ✅ Login endpoint responde correctamente!")
            try:
                json_response = response.json()
                print(f"   Response: {json.dumps(json_response, indent=2)}")
            except:
                print(f"   Response (text): {response.text[:200]}")
        elif response.status_code == 405:
            print("   ❌ Aún devuelve 405 Method Not Allowed")
        else:
            print(f"   ⚠️  Status code inesperado: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ No se puede conectar al servidor")
        print("   Asegúrate de que el servidor esté ejecutándose en puerto 8001")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n2. Probando GET {base_url}/...")
    try:
        # Probar GET / para verificar que el servidor funciona
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Servidor responde en raíz")
        else:
            print(f"   ⚠️  Status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n3. Probando GET {base_url}/docs...")
    try:
        # Probar GET /docs para verificar que swagger funciona
        response = requests.get(f"{base_url}/docs", timeout=5)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Documentación disponible")
        else:
            print(f"   ⚠️  Status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_admin_access():
    """Probar acceso al admin sin autenticación"""
    print(f"\n4. Probando acceso a /admin sin autenticación...")
    base_url = "http://localhost:8001"
    
    try:
        response = requests.get(f"{base_url}/admin", timeout=5, allow_redirects=False)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 307 and 'Location' in response.headers:
            print(f"   ✅ Redirige correctamente a: {response.headers['Location']}")
        elif response.status_code == 302 and 'Location' in response.headers:
            print(f"   ✅ Redirige correctamente a: {response.headers['Location']}")
        else:
            print(f"   ⚠️  Respuesta inesperada: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_login_endpoint()
    test_admin_access()
    
    print(f"\n📋 RESUMEN:")
    print("Si el login endpoint devuelve 200, el problema está resuelto!")
    print("Si aún devuelve 405, necesitamos investigar más.")
