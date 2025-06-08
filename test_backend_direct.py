import requests
import json

def test_login_endpoint_direct():
    print("🚀 TESTING LOGIN ENDPOINT DIRECTLY")
    print("=" * 40)
    
    # Test 1: Verificar página simple
    try:
        response = requests.get("http://localhost:8000/login-simple")
        print(f"✅ Login simple page: Status {response.status_code}")
        if response.status_code != 200:
            print(f"❌ Error: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error accediendo a login-simple: {e}")
        return False
    
    # Test 2: Probar login endpoint
    print("\n📍 Probando endpoint /login...")
    
    login_data = {
        "username": "testuser",
        "password": "Test123456"
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/login",
            data=login_data,
            headers=headers,
            allow_redirects=False,
            timeout=10
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📊 Response data keys: {list(data.keys())}")
                
                if 'access_token' in data:
                    print("✅ Access token presente")
                    print(f"📊 Token type: {data.get('token_type')}")
                    print(f"📊 Expires in: {data.get('expires_in')}")
                    
                    if 'user_info' in data:
                        user_info = data['user_info']
                        print(f"📊 Username: {user_info.get('username')}")
                        print(f"📊 Roles: {user_info.get('roles')}")
                    
                    print("✅ LOGIN ENDPOINT FUNCIONA CORRECTAMENTE")
                    return True
                else:
                    print("❌ No se encontró access_token en la respuesta")
                    print(f"📊 Response: {json.dumps(data, indent=2)}")
                    return False
                    
            except json.JSONDecodeError:
                print("❌ La respuesta no es JSON válido")
                print(f"📊 Response text: {response.text[:500]}")
                return False
        else:
            print(f"❌ Error status: {response.status_code}")
            print(f"📊 Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Error en request: {e}")
        return False

def test_authenticated_access():
    print("\n🔐 TESTING AUTHENTICATED ACCESS")
    print("=" * 40)
    
    # Primero hacer login para obtener token
    login_data = {
        "username": "testuser",
        "password": "Test123456"
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        login_response = requests.post(
            "http://localhost:8000/login",
            data=login_data,
            headers=headers
        )
        
        if login_response.status_code != 200:
            print("❌ No se pudo hacer login para el test de acceso autenticado")
            return False
            
        token_data = login_response.json()
        access_token = token_data.get('access_token')
        
        if not access_token:
            print("❌ No se obtuvo access token")
            return False
            
        print("✅ Token obtenido para test de acceso")
        
        # Probar acceso a endpoint autenticado
        auth_headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Test endpoint /admin
        admin_response = requests.get(
            "http://localhost:8000/admin",
            headers=auth_headers,
            allow_redirects=False
        )
        
        print(f"📊 Admin access status: {admin_response.status_code}")
        
        if admin_response.status_code == 200:
            print("✅ ACCESO AUTENTICADO A ADMIN FUNCIONA")
            return True
        elif admin_response.status_code == 500:
            print("❌ Error 500 en /admin")
            print(f"📊 Response: {admin_response.text[:500]}")
            return False
        else:
            print(f"❌ Status inesperado: {admin_response.status_code}")
            print(f"📊 Response: {admin_response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ Error en test de acceso autenticado: {e}")
        return False

if __name__ == "__main__":
    print("🔍 COMPREHENSIVE LOGIN TESTS")
    print("=" * 50)
    
    # Test 1: Login endpoint
    login_works = test_login_endpoint_direct()
    
    # Test 2: Authenticated access
    auth_works = test_authenticated_access()
    
    print("\n" + "=" * 50)
    print("📊 RESULTADOS FINALES:")
    print(f"Login Endpoint: {'✅ PASS' if login_works else '❌ FAIL'}")
    print(f"Authenticated Access: {'✅ PASS' if auth_works else '❌ FAIL'}")
    
    if login_works and auth_works:
        print("\n🎉 TODOS LOS TESTS PASARON - La autenticación funciona correctamente")
        print("El problema debe estar en el JavaScript del frontend")
    else:
        print("\n❌ HAY PROBLEMAS EN EL BACKEND - Revisar logs del servidor")
