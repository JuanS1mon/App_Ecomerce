import requests
import json

def test_endpoints():
    base_url = "http://localhost:8000"
    
    print("🧪 Probando endpoints de la aplicación...")
    
    # Probar endpoint raíz
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ GET / - Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Contenido: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ GET / - Error: {e}")
    
    # Probar endpoint de documentación
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"✅ GET /docs - Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Contenido: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ GET /docs - Error: {e}")
    
    # Probar endpoint de login page
    try:
        response = requests.get(f"{base_url}/loginpage")
        print(f"✅ GET /loginpage - Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Contenido: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ GET /loginpage - Error: {e}")
    
    # Probar endpoint de registro
    try:
        response = requests.get(f"{base_url}/registerpage")
        print(f"✅ GET /registerpage - Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Contenido: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ GET /registerpage - Error: {e}")

if __name__ == "__main__":
    test_endpoints()
