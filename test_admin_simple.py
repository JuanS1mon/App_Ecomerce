import requests

def test_admin_simple():
    print("🚀 TESTING ADMIN SIMPLE ENDPOINT")
    print("=" * 40)
    
    # Login para obtener token
    login_data = {
        "username": "testuser",
        "password": "Test123456"
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
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
    
    print(f"✅ Token obtenido")
    
    # Test admin-simple con Bearer token
    auth_headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'text/html',
    }
    
    try:
        response = requests.get(
            "http://localhost:8000/admin-simple",
            headers=auth_headers,
            timeout=10
        )
        
        print(f"📊 Admin-simple status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ ADMIN SIMPLE FUNCIONA!")
            print(f"📊 Response length: {len(response.text)} chars")
            print(f"📊 Content type: {response.headers.get('content-type')}")
        else:
            print(f"❌ Error: {response.text[:300]}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test con cookies
    print("\n🔍 Testing admin-simple con cookies...")
    
    session = requests.Session()
    session.post("http://localhost:8000/login", data=login_data, headers=headers)
    
    try:
        response = session.get("http://localhost:8000/admin-simple", timeout=10)
        print(f"📊 Admin-simple con cookies status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ ADMIN SIMPLE CON COOKIES FUNCIONA!")
        else:
            print(f"❌ Error con cookies: {response.text[:300]}")
                
    except Exception as e:
        print(f"❌ Exception con cookies: {e}")

if __name__ == "__main__":
    test_admin_simple()
