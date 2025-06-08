import requests
import json

def test_admin_debug_endpoint():
    print("🔧 TESTING ADMIN DEBUG ENDPOINT")
    print("=" * 40)
    
    # Obtener token
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
    
    # Test admin-debug con Bearer token
    auth_headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
    }
    
    try:
        response = requests.get(
            "http://localhost:8000/admin-debug",
            headers=auth_headers,
            timeout=10
        )
        
        print(f"📊 Admin-debug status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {json.dumps(data, indent=2)}")
        else:
            try:
                error_data = response.json()
                print(f"❌ Error response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"❌ Error text: {response.text}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # También test con cookies
    print("\n🔍 Testing con cookies...")
    
    session = requests.Session()
    session.post("http://localhost:8000/login", data=login_data, headers=headers)
    
    try:
        response = session.get("http://localhost:8000/admin-debug", timeout=10)
        print(f"📊 Admin-debug con cookies status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success con cookies: {json.dumps(data, indent=2)}")
        else:
            try:
                error_data = response.json()
                print(f"❌ Error con cookies: {json.dumps(error_data, indent=2)}")
            except:
                print(f"❌ Error text con cookies: {response.text}")
                
    except Exception as e:
        print(f"❌ Exception con cookies: {e}")

if __name__ == "__main__":
    test_admin_debug_endpoint()
