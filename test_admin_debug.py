import requests
import json

def test_admin_debug():
    print("🔧 DEBUGGING ADMIN ENDPOINT")
    print("=" * 40)
    
    # Obtener token
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
            print("❌ Login falló")
            return
            
        token_data = login_response.json()
        access_token = token_data.get('access_token')
        
        print(f"✅ Token obtenido: {access_token[:50]}...")
        
        # Verificar diferentes formas de enviar el token
        
        # 1. Como Bearer token en Authorization header
        print("\n🔍 Test 1: Bearer token en Authorization header")
        auth_headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(
                "http://localhost:8000/admin",
                headers=auth_headers,
                allow_redirects=False,
                timeout=10
            )
            print(f"📊 Status: {response.status_code}")
            print(f"📊 Content-Type: {response.headers.get('content-type', 'N/A')}")
            
            if response.status_code == 500:
                print(f"❌ Error 500: {response.text[:500]}")
            elif response.status_code == 200:
                print("✅ Admin access successful!")
                print(f"📊 Response length: {len(response.text)} chars")
            else:
                print(f"📊 Response: {response.text[:300]}")
                
        except Exception as e:
            print(f"❌ Error en request: {e}")
        
        # 2. Con cookies (el login debería haber seteado una cookie)
        print("\n🔍 Test 2: Usando cookies desde login")
        
        # Hacer una nueva session para conservar cookies
        session = requests.Session()
        
        login_response = session.post(
            "http://localhost:8000/login",
            data=login_data,
            headers=headers
        )
        
        print(f"📊 Login cookies: {list(session.cookies.keys())}")
        
        try:
            response = session.get(
                "http://localhost:8000/admin",
                allow_redirects=False,
                timeout=10
            )
            print(f"📊 Status con cookies: {response.status_code}")
            
            if response.status_code == 500:
                print(f"❌ Error 500 con cookies: {response.text[:500]}")
            elif response.status_code == 200:
                print("✅ Admin access con cookies successful!")
            else:
                print(f"📊 Response con cookies: {response.text[:300]}")
                
        except Exception as e:
            print(f"❌ Error con cookies: {e}")
            
        # 3. Test de otro endpoint protegido para comparar
        print("\n🔍 Test 3: Verificando otros endpoints")
        
        try:
            current_user_response = requests.get(
                "http://localhost:8000/usuarios/current",
                headers=auth_headers,
                timeout=10
            )
            print(f"📊 Current user status: {current_user_response.status_code}")
            
            if current_user_response.status_code == 200:
                data = current_user_response.json()
                print(f"✅ Current user works: {data.get('username', 'N/A')}")
            else:
                print(f"❌ Current user error: {current_user_response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Error en current user: {e}")
            
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_admin_debug()
