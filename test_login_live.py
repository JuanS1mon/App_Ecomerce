#!/usr/bin/env python3
"""
Script simple para probar el endpoint de login
"""
import requests
import json

def test_login_endpoint():
    """Prueba el endpoint de login directamente"""
    print("🧪 PRUEBA DIRECTA DEL ENDPOINT DE LOGIN")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ Servidor FastAPI está ejecutándose")
        else:
            print("⚠️  Servidor responde pero no en /docs")
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. ¿Está ejecutándose en localhost:8000?")
        print("   Ejecuta: uvicorn sql_app.main:app --reload")
        return
    except Exception as e:
        print(f"❌ Error conectando: {e}")
        return
    
    print()
    
    # Datos de login de prueba
    login_data = {
        "username": "admin",
        "password": "admin"
    }
    
    print(f"📝 Datos de login: {login_data}")
    print()
    
    # Test 1: POST /login con form data (OAuth2 standard)
    print("🔄 TEST 1: POST /login con form data")
    print("-" * 40)
    try:
        response = requests.post(
            f"{base_url}/login",
            data=login_data,  # form-encoded
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers Allow: {response.headers.get('Allow', 'No Allow header')}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'No Content-Type')}")
        
        if response.status_code == 200:
            print("   ✅ LOGIN EXITOSO!")
            try:
                data = response.json()
                if "access_token" in data:
                    print(f"   🎫 Token: {data['access_token'][:30]}...")
                print(f"   📄 Response: {json.dumps(data, indent=2)}")
            except:
                print(f"   📄 Response text: {response.text}")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    print()
    
    # Test 2: OPTIONS /login
    print("🔄 TEST 2: OPTIONS /login")
    print("-" * 40)
    try:
        response = requests.options(f"{base_url}/login")
        print(f"   Status: {response.status_code}")
        print(f"   Headers Allow: {response.headers.get('Allow', 'No Allow header')}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    print()
    
    # Test 3: GET /login (debería fallar)
    print("🔄 TEST 3: GET /login (debería dar 405)")
    print("-" * 40)
    try:
        response = requests.get(f"{base_url}/login")
        print(f"   Status: {response.status_code}")
        print(f"   Headers Allow: {response.headers.get('Allow', 'No Allow header')}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    print()
    print("=" * 50)
    print("🏁 PRUEBA COMPLETADA")
    print()
    print("📋 INSTRUCCIONES:")
    print("   1. Si el servidor no está corriendo:")
    print("      cd sql_app && uvicorn main:app --reload")
    print("   2. Si obtienes error 422, prueba con otras credenciales")
    print("   3. Si obtienes error 405, este es el problema que necesitamos resolver")

if __name__ == "__main__":
    test_login_endpoint()
